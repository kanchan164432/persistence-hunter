#include <iostream>
#include <fstream>
#include <vector>
#include <chrono>
#include <boost/multiprecision/cpp_int.hpp>
#include <omp.h>

using namespace boost::multiprecision;
using namespace std;

// Calculates Base 17 Multiplicative Persistence
int get_persistence_b17(cpp_int n) {
    int steps = 0;
    while (n >= 17) {
        cpp_int prod = 1, temp = n;
        while (temp > 0) {
            prod *= (temp % 17);
            temp /= 17;
        }
        n = prod;
        steps++;
    }
    return steps;
}

int main() {
    int current_E = 1;
    int global_max_p = -1;

    // Load state (current exponent depth and highest persistence found so far)
    ifstream state_in("state_b17.txt");
    if (state_in >> current_E) {
        state_in >> global_max_p;
        state_in.close();
    }

    auto start_time = chrono::high_resolution_clock::now();
    double run_duration = 4.5 * 3600; // 4.5 hours execution window

    cout << "Resuming Base 17 Search from E = " << current_E 
         << " (Previous Max Persistence: " << global_max_p << ")..." << endl;

    while (true) {
        auto now = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed = now - start_time;
        if (elapsed.count() >= run_duration) break;

        // Pre-compute prime powers for current_E to eliminate expensive pow() calls
        vector<cpp_int> p2(current_E + 1), p3(current_E + 1), p5(current_E + 1),
                        p7(current_E + 1), p11(current_E + 1), p13(current_E + 1);
        p2[0] = p3[0] = p5[0] = p7[0] = p11[0] = p13[0] = 1;
        for (int i = 1; i <= current_E; ++i) {
            p2[i] = p2[i - 1] * 2;
            p3[i] = p3[i - 1] * 3;
            p5[i] = p5[i - 1] * 5;
            p7[i] = p7[i - 1] * 7;
            p11[i] = p11[i - 1] * 11;
            p13[i] = p13[i - 1] * 13;
        }

        int local_max_p = -1;

        #pragma omp parallel for reduction(max:local_max_p) schedule(dynamic)
        for (int a = 0; a <= current_E; ++a) {
            for (int b = 0; b <= current_E - a; ++b) {
                for (int c = 0; c <= current_E - a - b; ++c) {
                    for (int d = 0; d <= current_E - a - b - c; ++d) {
                        for (int e = 0; e <= current_E - a - b - c - d; ++e) {
                            int f = current_E - a - b - c - d - e;

                            // Fast multiplication using pre-computed powers
                            cpp_int P1 = p2[a] * p3[b] * p5[c] * p7[d] * p11[e] * p13[f];

                            int p = 1 + get_persistence_b17(P1);

                            if (p > local_max_p) local_max_p = p;

                            if (p >= 18) { // Base 17 World Record threshold
                                #pragma omp critical
                                {
                                    cout << "🚨 WORLD RECORD: Base 17 Persistence " << p 
                                         << " at E=" << current_E << "!" << endl;
                                }
                            }
                        }
                    }
                }
            }
        }

        if (local_max_p > global_max_p) {
            global_max_p = local_max_p;
            cout << "New High Base 17 Persistence: " << global_max_p << " at E=" << current_E << endl;
        }

        current_E++;
    }

    auto end_time = chrono::high_resolution_clock::now();
    chrono::duration<double> total_elapsed = end_time - start_time;

    // Save persistent state for next run (E level and global record)
    ofstream state_out("state_b17.txt");
    state_out << current_E << " " << global_max_p;
    state_out.close();

    // Save output JSON for workflow reporter
    ofstream out("results_b17.json");
    out << "{\n";
    out << "  \"max_persistence\": " << global_max_p << ",\n";
    out << "  \"ended_E\": " << (current_E - 1) << ",\n";
    out << "  \"elapsed_seconds\": " << total_elapsed.count() << "\n";
    out << "}\n";
    out.close();

    cout << "Execution complete. Reached E = " << (current_E - 1) 
         << " in " << total_elapsed.count() << " seconds." << endl;

    return 0;
}
