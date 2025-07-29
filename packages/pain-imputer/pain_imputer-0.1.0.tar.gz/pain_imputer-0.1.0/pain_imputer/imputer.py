import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from tensorflow.keras.layers import Dense, Input, BatchNormalization
from tensorflow.keras.models import Model
from tensorflow.keras.callbacks import EarlyStopping

class PAINImputer:
    """Precision Adaptive Imputation Network (PAIN) for imputing missing data in numeric datasets."""
    
    def __init__(self, n_iterations=5, n_neighbors=5, n_estimators=100, 
                 encoder_layers=[64, 32, 16], random_state=42):
        self.n_iterations = n_iterations
        self.n_neighbors = n_neighbors
        self.n_estimators = n_estimators
        self.encoder_layers = encoder_layers
        self.random_state = random_state
        self.scaler = StandardScaler()

    def _baseline_imputation(self, X, missing_mask):
        """Perform baseline imputation only on missing values."""
        X_filled = X.copy()
        if np.any(missing_mask):
            mean_imputer = SimpleImputer(strategy='mean')
            mean_imputed = mean_imputer.fit_transform(X)
            median_imputer = SimpleImputer(strategy='median')
            median_imputed = median_imputer.fit_transform(X)
            knn_imputer = KNNImputer(n_neighbors=self.n_neighbors)
            knn_imputed = knn_imputer.fit_transform(X)
            
            missing_ratio = np.mean(missing_mask)
            weights = [0.3 * (1 - missing_ratio), 0.3 * (1 - missing_ratio), 0.4 * missing_ratio]
            X_weighted = weights[0] * mean_imputed + weights[1] * median_imputed + weights[2] * knn_imputed
            X_filled[missing_mask] = X_weighted[missing_mask]
        print("After baseline:\n", X_filled)
        return X_filled

    def _build_autoencoder(self, input_dim):
        """Build a symmetric autoencoder for neural imputation."""
        input_layer = Input(shape=(input_dim,))
        encoded = input_layer
        for units in self.encoder_layers:
            encoded = Dense(units, activation='relu')(encoded)
            encoded = BatchNormalization()(encoded)
        decoded = encoded
        for units in reversed(self.encoder_layers[:-1]):
            decoded = Dense(units, activation='relu')(decoded)
            decoded = BatchNormalization()(decoded)
        output_layer = Dense(input_dim, activation='linear')(decoded)
        autoencoder = Model(inputs=input_layer, outputs=output_layer)
        autoencoder.compile(optimizer='adam', loss='mse')
        return autoencoder

    def _neural_imputation(self, X, missing_mask):
        """Impute missing values using an autoencoder, preserving non-missing."""
        X_filled = X.copy()
        if np.any(missing_mask):
            autoencoder = self._build_autoencoder(X.shape[1])
            early_stopping = EarlyStopping(monitor='loss', patience=10, restore_best_weights=True)
            X_train = X.copy()
            col_means = np.nanmean(X, axis=0)
            X_train[missing_mask] = col_means[np.where(missing_mask)[1]]
            autoencoder.fit(X_train, X_train, epochs=100, batch_size=32, verbose=0, 
                            callbacks=[early_stopping])
            imputed = autoencoder.predict(X_train, verbose=0)
            X_filled[missing_mask] = imputed[missing_mask]
        print("After neural:\n", X_filled)
        return X_filled

    def _random_forest_imputation(self, X, missing_mask):
        """Impute missing values using Random Forest, preserving non-missing."""
        X_filled = X.copy()
        for col in range(X.shape[1]):
            if np.any(missing_mask[:, col]):
                known = ~missing_mask[:, col]
                missing = missing_mask[:, col]
                X_train = np.delete(X_filled[known], col, axis=1)
                y_train = X_filled[known, col]
                X_test = np.delete(X_filled[missing], col, axis=1)
                rf = RandomForestRegressor(n_estimators=self.n_estimators, 
                                          max_depth=10, min_samples_leaf=5,
                                          random_state=self.random_state)
                rf.fit(X_train, y_train)
                X_filled[missing, col] = rf.predict(X_test)
        print("After RF:\n", X_filled)
        return X_filled

    def _refinement(self, X_imputed, X_orig, missing_mask):
        """Refine imputed values, ensuring non-missing are preserved."""
        X_refined = X_orig.copy()
        if np.any(missing_mask):
            X_temp = X_imputed.copy()
            for col in range(X_temp.shape[1]):
                if np.any(missing_mask[:, col]):
                    q1, q3 = np.nanpercentile(X_orig[:, col], [25, 75])
                    iqr = q3 - q1
                    lower = q1 - 1.5 * iqr
                    upper = q3 + 1.5 * iqr
                    col_values = X_temp[missing_mask[:, col], col]
                    X_refined[missing_mask[:, col], col] = np.clip(col_values, lower, upper)
        print("After refinement:\n", X_refined)
        return X_refined

    def fit_transform(self, X):
        """
        Impute missing values in X, preserving non-missing values.
        
        Parameters:
        - X: Input data (numpy array or pandas DataFrame) with missing values.
        
        Returns:
        - Imputed data (same type as input).
        """
        print("Starting fit_transform")
        if isinstance(X, pd.DataFrame):
            X_array = X.values.astype(float)
            columns = X.columns
        else:
            X_array = np.array(X, dtype=float)
            columns = None
        
        missing_mask = np.isnan(X_array)
        X_orig = X_array.copy()
        
        # Step 1: Baseline imputation
        X_baseline = self._baseline_imputation(X_orig, missing_mask)
        
        # Step 2: Advanced imputation with iterations
        X_final = X_baseline.copy()
        for i in range(self.n_iterations):
            print(f"Iteration {i+1}:")
            X_rf = self._random_forest_imputation(X_final, missing_mask)
            X_neural = self._neural_imputation(X_rf, missing_mask)
            missing_ratio = np.mean(missing_mask)
            weights = [0.7, 0.3] if missing_ratio < 0.3 else [0.4, 0.6]
            X_combined = weights[0] * X_rf + weights[1] * X_neural
            X_combined[~missing_mask] = X_orig[~missing_mask]  # Preserve non-missing
            X_final = self._refinement(X_combined, X_orig, missing_mask)
        
        if columns is not None:
            return pd.DataFrame(X_final, columns=columns)
        return X_final