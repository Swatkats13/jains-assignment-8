import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss
from scipy.spatial.distance import cdist
import os
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for Flask compatibility

result_dir = "results"
os.makedirs(result_dir, exist_ok=True)

def generate_ellipsoid_clusters(distance, n_samples=100, cluster_std=0.5):
    """
    Generate two clusters of points, shifting the second cluster along y = -x direction.
    """
    np.random.seed(0)
    covariance_matrix = np.array([[cluster_std, cluster_std * 0.8], 
                                   [cluster_std * 0.8, cluster_std]])
    
    # Generate the first cluster (class 0)
    X1 = np.random.multivariate_normal(mean=[1, 1], cov=covariance_matrix, size=n_samples)
    y1 = np.zeros(n_samples)

    # Generate the second cluster (class 1)
    # Shift along y = -x direction (subtract distance from x and add distance to y)
    X2 = np.random.multivariate_normal(mean=[1 - distance, 1 + distance], cov=covariance_matrix, size=n_samples)
    y2 = np.ones(n_samples)

    # Combine the clusters into one dataset
    X = np.vstack((X1, X2))
    y = np.hstack((y1, y2))
    return X, y

# Function to fit logistic regression and extract coefficients
def fit_logistic_regression(X, y):
    model = LogisticRegression()
    model.fit(X, y)
    beta0 = model.intercept_[0]
    beta1, beta2 = model.coef_[0]
    return model, beta0, beta1, beta2

def calculate_logistic_loss(model, X, y):
    y_pred_proba = model.predict_proba(X)
    return log_loss(y, y_pred_proba)

def do_experiments(start, end, step_num):
    # Set up experiment parameters
    shift_distances = np.linspace(start, end, step_num)  # Range of shift distances
    beta0_list, beta1_list, beta2_list, slope_list, intercept_list, loss_list, margin_widths = [], [], [], [], [], [], []

    n_cols = 2  # Number of columns for subplots
    n_rows = (step_num + n_cols - 1) // n_cols  # Calculate required rows
    plt.figure(figsize=(20, n_rows * 10))  # Adjust figure size

    # Run experiments for each shift distance
    for i, distance in enumerate(shift_distances, 1):
        X, y = generate_ellipsoid_clusters(distance=distance)
        model, beta0, beta1, beta2 = fit_logistic_regression(X, y)
        
        # Calculate slope and intercept for decision boundary
        slope = -beta1 / beta2
        intercept = -beta0 / beta2

        # Calculate logistic loss
        loss = calculate_logistic_loss(model, X, y)

        # Calculate margin width (2 / ||beta||)
        margin_width = 2 / np.sqrt(beta1**2 + beta2**2)

        # Append results to lists
        beta0_list.append(beta0)
        beta1_list.append(beta1)
        beta2_list.append(beta2)
        slope_list.append(slope)
        intercept_list.append(intercept)
        loss_list.append(loss)
        margin_widths.append(margin_width)

        # Plot the dataset and decision boundary
        plt.subplot(n_rows, n_cols, i)
        plt.scatter(X[y == 0][:, 0], X[y == 0][:, 1], color='blue', label='Class 0')
        plt.scatter(X[y == 1][:, 0], X[y == 1][:, 1], color='red', label='Class 1')
        x_min, x_max = X[:, 0].min() - 1, X[:, 0].max() + 1
        y_min, y_max = X[:, 1].min() - 1, X[:, 1].max() + 1
        xx, yy = np.meshgrid(np.linspace(x_min, x_max, 200), np.linspace(y_min, y_max, 200))
        Z = model.predict_proba(np.c_[xx.ravel(), yy.ravel()])[:, 1]
        Z = Z.reshape(xx.shape)
        plt.contourf(xx, yy, Z, levels=[0.5, 1.0], colors=['lightblue', 'salmon'], alpha=0.3)
        plt.xlabel("x1")
        plt.ylabel("x2")
        plt.title(f"Shift Distance = {distance:.2f}")

        # Display decision boundary and margin width on the plot
        equation_text = f"{beta0:.2f} + {beta1:.2f} * x1 + {beta2:.2f} * x2 = 0\nx2 = {slope:.2f} * x1 + {intercept:.2f}"
        margin_text = f"Margin Width: {margin_width:.2f}"
        plt.text(x_min + 0.1, y_max - 1.0, equation_text, fontsize=12, color="black")
        plt.text(x_min + 0.1, y_max - 1.5, margin_text, fontsize=12, color="black")

    plt.tight_layout()
    plt.savefig(f"{result_dir}/dataset.png")

    # Plot results across shift distances
    plt.figure(figsize=(18, 15))

    # Plot beta0
    plt.subplot(3, 3, 1)
    plt.plot(shift_distances, beta0_list, marker='o')
    plt.title("Shift Distance vs Beta0")
    plt.xlabel("Shift Distance")
    plt.ylabel("Beta0")

    # Plot beta1
    plt.subplot(3, 3, 2)
    plt.plot(shift_distances, beta1_list, marker='o')
    plt.title("Shift Distance vs Beta1 (Coefficient for x1)")
    plt.xlabel("Shift Distance")
    plt.ylabel("Beta1")

    # Plot beta2
    plt.subplot(3, 3, 3)
    plt.plot(shift_distances, beta2_list, marker='o')
    plt.title("Shift Distance vs Beta2 (Coefficient for x2)")
    plt.xlabel("Shift Distance")
    plt.ylabel("Beta2")

    # Plot slope
    plt.subplot(3, 3, 4)
    plt.plot(shift_distances, slope_list, marker='o')
    plt.title("Shift Distance vs Slope (Beta1 / Beta2)")
    plt.xlabel("Shift Distance")
    plt.ylabel("Slope")

    # Plot intercept
    plt.subplot(3, 3, 5)
    plt.plot(shift_distances, intercept_list, marker='o')
    plt.title("Shift Distance vs Intercept (Beta0 / Beta2)")
    plt.xlabel("Shift Distance")
    plt.ylabel("Intercept")

    # Plot logistic loss
    plt.subplot(3, 3, 6)
    plt.plot(shift_distances, loss_list, marker='o')
    plt.title("Shift Distance vs Logistic Loss")
    plt.xlabel("Shift Distance")
    plt.ylabel("Logistic Loss")

    # Plot margin width
    plt.subplot(3, 3, 7)
    plt.plot(shift_distances, margin_widths, marker='o')
    plt.title("Shift Distance vs Margin Width")
    plt.xlabel("Shift Distance")
    plt.ylabel("Margin Width")

    plt.tight_layout()
    plt.savefig(f"{result_dir}/parameters_vs_shift_distance.png")
