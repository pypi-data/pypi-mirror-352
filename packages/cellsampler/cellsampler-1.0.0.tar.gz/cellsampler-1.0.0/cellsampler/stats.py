from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment


def calculate_confusion_matrix_from_centers(
    gt_centers, pred_centers, distance_threshold
):
    # Calculate pairwise distances between ground truth and predicted centers
    distance_matrix = cdist(gt_centers, pred_centers)

    # Solve the assignment problem to find the best matches
    row_ind, col_ind = linear_sum_assignment(distance_matrix)

    # Initialize counts
    true_positives = 0
    false_positives = 0
    false_negatives = 0
    true_negatives = 0  # Note: TN is usually not applicable in this context

    matched_gt_indices = set()
    matched_pred_indices = set()

    for i, j in zip(row_ind, col_ind):
        if distance_matrix[i, j] <= distance_threshold:
            true_positives += 1
            matched_gt_indices.add(i)
            matched_pred_indices.add(j)
        else:
            # If distance is greater than threshold, it's not a match
            false_negatives += 1

    # Count false positives
    # (predicted centers with no matching ground truth center)
    false_positives += len(pred_centers) - len(matched_pred_indices)

    # Count false negatives
    # (ground truth centers with no matching predicted center)
    false_negatives += len(gt_centers) - len(matched_gt_indices)

    # True negatives aren't typically defined in this context
    # but would refer to areas with no detected cells in both images

    return true_positives, false_positives, false_negatives, true_negatives
