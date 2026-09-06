#include <iostream>
#include <fstream>
#include <chrono>
#include <boost/multiprecision/cpp_int.hpp>
#include <omp.h>

using namespace boost::multiprecision;
using namespace std;

// Calculates Base 15 Multiplicative Persistence
int get_persistence_b15(cpp_int n) {
    int steps = 0;
    while (n >= 15) {
        cpp_int prod = 1;
        cpp_int temp = n;
        while (temp > 0) {
            prod *= (temp % 15);
            temp /= 15;
        }
        n = prod;
        steps++;
    }
    return steps;
}

int main() {
    int start_E = 1;
    int end_E = 100; // Deep search depth for C++
    int max_p = -1;

    cout << "Starting C++ Base 15 Search (E = " << start_E << " to " << end_E << ")..." << endl;
    auto start_time = chrono::high_resolution_clock::now();

    for (int E = start_E; E <= end_E; ++E) {
        int local_max_p = -1;

        #pragma omp parallel for reduction(max:local_max_p) schedule(dynamic)
        for (int a = 0; a <= E; ++a) {
            for (int b = 0; b <= E - a; ++b) {
                for (int c = 0; c <= E - a - b; ++c) {
                    // Zero-Trap Optimization: 15 = 3 * 5. Skip if both factors exist.
                    if (b > 0 && c > 0) continue;

                    for (int d = 0; d <= E - a - b - c; ++d) {
                        for (int e = 0; e <= E - a - b - c - d; ++e) {
                            int f = E - a - b - c - d - e;

                            cpp_int P1 = pow(cpp_int(2), a) * pow(cpp_int(3), b) *
                                        pow(cpp_int(5), c) * pow(cpp_int(7), d) *
                                        pow(cpp_int(11), e) * pow(cpp_int(13), f);

                            int p = 1 + get_persistence_b15(P1);

                            if (p > local_max_p) {
                                local_max_p = p;
                            }
                            if (p >= 12) {
                                #pragma omp critical
                                {
                                    cout << "🚨 WORLD RECORD: Base 15 Persistence " << p 
                                         << " at E=" << E << "!" << endl;
                                }
                            }
                        }
                    }
                }
            }
        }
        if (local_max_p > max_p) {
            max_p = local_max_p;
        }
    }

    auto end_time = chrono::high_resolution_clock::now();
    chrono::duration<double> elapsed = end_time - start_time;

    // Save output to JSON for Python email reporter
    ofstream out("results_b15.json");
    out << "{\n";
    out << "  \"max_persistence\": " << max_p << ",\n";
    out << "  \"ended_E\": " << end_E << ",\n";
    out << "  \"elapsed_seconds\": " << elapsed.count() << "\n";
    out << "}\n";
    out.close();

    cout << "Search complete. Saved results to results_b15.json." << endl;
    return 0;
}
