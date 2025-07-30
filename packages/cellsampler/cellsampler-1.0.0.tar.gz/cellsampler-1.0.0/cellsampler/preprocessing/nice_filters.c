// gcc -shared -fpic nice_filters.c -o nice_filters.so
//

#include <math.h>
#include <stdint.h>
#include <stdlib.h>

// Function to compare values (needed for qsort)
int compare(const void *a, const void *b) {
    double diff = (*(double*)a - *(double*)b);
    if (diff > 0) return 1;
    else if (diff < 0) return -1;
    return 0;
}


// Function to find the median of an array of doubles
double findMedian(double arr[], int n) {
    // Sort the array
    qsort(arr, n, sizeof(double), compare);

    // If the number of elements is odd, return the middle element
    if (n % 2 != 0)
        return arr[n/2];

    // If the number of elements is even, return the average of the two middle elements
    return (arr[(n-1)/2] + arr[n/2]) / 2.0;
}


// Function to calculate Median Absolute Deviation (MAD)
double calculateMAD(double arr[], int n) {
    double median = findMedian(arr, n);
    double deviations[n];

    // Calculate absolute deviations from the median
    for (int i = 0; i < n; i++) {
        deviations[i] = fabs(arr[i] - median);
    }

    // Find the median of absolute deviations
    return findMedian(deviations, n);
}


int mad_filter(
    double * buffer,
    intptr_t filter_size,
    double * return_value,
    void * user_data
) {
    *return_value = calculateMAD(buffer, filter_size);
    // return 1 to indicate success (CPython convention)
    return 1;
}
