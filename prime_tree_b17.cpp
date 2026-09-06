#include <iostream>
#include <fstream>
#include <chrono>
#include <boost/multiprecision/cpp_int.hpp>
#include <omp.h>

using namespace boost::multiprecision;
using namespace std;

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
    ifstream state_in("state_b17.txt");
    if (state_in >> current_E) state_in.close();

    int max_p = -1;
    auto start_time = chrono::high_resolution_clock::now();
    double run_duration = 4.5 * 3600; // Run continuously for 4.5 hours

    cout << "Resuming C++ Base 17 Search from E = " << current_E << "..." << endl;

    while (true) {
        auto now = chrono::high_resolution_clock::now();
        chrono::duration<double> elapsed = now - start_time;
        if (elapsed.count() >= run_duration) break;

        int local_max_p = -1;
        #pragma omp parallel for reduction(max:local_max_p) schedule(dynamic)
        for (int a = 0; a <= current_E; ++a) {
            for (int b = 0; b <= current_E - a; ++b) {
                for (int c = 0; c <= current_E - a - b; ++c) {
                    for (int d = 0; d <= current_E - a - b - c; ++d) {
                        for (int e = 0; e <= current_E - a - b - c - d; ++e) {
                            int f = current_E - a - b - c - d - e;
                            cpp_int P1 = pow(cpp_int(2), a) * pow(cpp_int(3), b) *
                                        pow(cpp_int(5), c) * pow(cpp_int(7), d) *
                                        pow(cpp_int(11), e) * pow(cpp_int(13), f);
                            int p = 1 + get_persistence_b17(P1);
                            if (p > local_max_p) local_max_p = p;
                            if (p >= 18) { // Record threshold for Base 17
                                #pragma omp critical
                                cout << "🚨 WORLD RECORD: Base 17 Persistence " << p << " at E=" << current_E << "!" << endl;
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
    ofstream state_out("state_b17.txt");
    state_out << current_E;
    state_out.close();

    ofstream out("results_b17.json");
    out << "{\n  \"max_persistence\": " << max_p << ",\n  \"ended_E\": " << (current_E - 1) << "\n}\n";
    out.close();

    return 0;
}
