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
        cpp_int prod = 1, temp = n;
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
    int current_E = 1;
    ifstream state_in("state_b15.txt");
    if (state_in >> current_E) state_in.close();

    int max_p = -1;
    auto start_time = chrono::high_resolution_clock::now();
    double run_duration = 4.5 * 3600; // Run continuously for 4.5 hours

    cout << "Resuming C++ Base 15 Search from Exponent Sum E = " << current_E << "..." << endl;

    while (true) {
        auto now = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed = now - start_time;
        if (elapsed.count() >= run_duration) break;

        int local_max_p = -1;

        #pragma omp parallel for reduction(max:local_max_p) schedule(dynamic)
        for (int a = 0; a <= current_E; ++a) {
            for (int b = 0; b <= current_E - a; ++b) {
                for (int c = 0; c <= current_E - a - b; ++c) {
                    // Zero-Trap Optimization: 15 = 3 * 5. 
                    // Skip any branch containing both factors 3 and 5 (ends in 0 in Base 15).
                    if (b > 0 && c > 0) continue;

                    for (int d = 0; d <= current_E - a - b - c; ++d) {
                        for (int e = 0; e <= current_E - a - b - c - d; ++e) {
                            int f = current_E - a - b - c - d - e;

                            cpp_int P1 = pow(cpp_int(2), a) * pow(cpp_int(3), b) *
                                        pow(cpp_int(5), c) * pow(cpp_int(7), d) *
                                        pow(cpp_int(11), e) * pow(cpp_int(13), f);

                            int p = 1 + get_persistence_b15(P1);

                            if (p > local_max_p) local_max_p = p;

                            // Threshold set to >= 12 (Current known Base 15 max is 11)
                            if (p >= 12) {
                                #pragma omp critical
                                {
                                    cout << "🚨 WORLD RECORD: Base 15 Persistence " << p 
                                         << " at E=" << current_E << "!" << endl;
                                }
                            }
                        }
                    }
                }
            }
        }
        if (local_max_p > max_p) max_p = local_max_p;
        current_E++;
    }

    // Save state for next run
    ofstream state_out("state_b15.txt");
    state_out << current_E;
    state_out.close();

    ofstream out("results_b15.json");
    out << "{\n  \"max_persistence\": " << max_p << ",\n  \"ended_E\": " << (current_E - 1) << "\n}\n";
    out.close();

    cout << "Search paused after 4.5 hours at E = " << current_E << ". Saved state to state_b15.txt." << endl;
    return 0;
}
