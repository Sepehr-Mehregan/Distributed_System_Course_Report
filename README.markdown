# 🚗 Distributed Systems Course Report: Task Allocation for Autonomous Fleets

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Course](https://img.shields.io/badge/Course-Distributed%20Systems-green)](https://example.com)

Welcome to the **Distributed Systems Course Report** repository! 🎉 This project dives into task allocation algorithms for autonomous vehicle fleets, comparing **auction-based** and **Q-learning** approaches in a dynamic environment. Built with Python 🐍, it simulates a fleet navigating tasks with battery constraints and charger access, offering insights into efficiency and real-world applicability.

🔍 **Why this matters**: Efficient task allocation is key to optimizing logistics, robotics, and fleet management. Our report and code explore how decentralized algorithms handle dynamic challenges, with a focus on performance and ethics.

---

## 📖 Project Overview

This repository contains the code and report for a course project evaluating task allocation strategies for autonomous vehicle fleets. We implemented and compared:
- **Auction-Based Allocation** 💸: Vehicles bid on tasks based on engagement time, urgency, and battery levels.
- **Q-Learning Allocation** 🧠: Reinforcement learning optimizes task assignments over time.
- **Greedy Baselines** ⚡: Basic and position-update strategies for comparison.
- **Auction with Charger** 🔌: Extends auction to include charger routing.

The simulations use Python with NumPy, Pandas, and Matplotlib, modeling dynamic task arrivals, battery constraints, and charger access. The report (`Task Allocation Algorithms Report.pdf`) details the methodology, results, and ethical considerations.

---

## 📂 Repository Structure

- **`DataGenerationDynamic.py`**: Generates vehicle 🚗 and task 📋 datasets (positions, battery, urgency, etc.).
- **`fleet_greedy_allocationDynamic.py`**: Implements greedy strategies (basic, position-update).
- **`Auction_Allocation.py`**: Auction algorithm without charger integration.
- **`Auction_with_Charger.py`**: Auction with charger routing.
- **`QL_Allocation.py`**: Q-learning-based allocation.
- **`Report.ipynb`**: Jupyter notebook for simulations and visualizations 📊.
- **`Task Allocation Algorithms Report.pdf`**: Full report with analysis and findings.
- **`vehicle/`**, **`task/`**, **`randomtask/`**: Stores generated CSV data.

---

## 🛠️ Installation

Get started in a few simple steps! 🚀

1. **Clone the repository**:
   ```bash
   git clone https://github.com/<your-username>/Distributed_Systems_Course_Report.git
   cd Distributed_Systems_Course_Report
   ```

2. **Install dependencies**:
   Ensure Python 3.8+ is installed, then run:
   ```bash
   pip install numpy pandas matplotlib
   ```

3. **Optional: Jupyter Notebook**:
   To run `Report.ipynb`, install Jupyter:
   ```bash
   pip install jupyter
   ```

---

## 🚀 Usage

1. **Run Simulations**:
   - Launch Jupyter Notebook:
     ```bash
     jupyter notebook Report.ipynb
     ```
   - Execute cells to generate data, run simulations, and plot metrics (e.g., tasks completed, engagement time).
   - Results are saved as CSVs in `vehicle`, `task`, and `randomtask` directories.

2. **Customize Parameters**:
   - Edit `TIME_STEPS`, `NEW_TASK_PROB`, or `URGENCY_INCREMENT` in `Report.ipynb`.
   - Modify vehicle/task counts in `DataGenerationDynamic.py`.

3. **View Results**:
   - Check plots in the notebook (see Figure 1 in the report).
   - Metrics include task throughput, engagement time, and idle time.

4. **Read the Report**:
   - Open `Task Allocation Algorithms Report.pdf` for detailed analysis and insights.

---

## 📊 Key Findings

- **Auction without Charger (AWC)** 💪: Allocates the most tasks, ideal for high-throughput scenarios.
- **Auction with Charger (AC)** 🔌: Lower performance due to charger overhead; needs optimization.
- **Q-Learning (QL)** 🧠: Matches greedy baselines, with potential for improvement via exploration.
- **Greedy Baselines** ⚡: Consistent, with position-update slightly better than basic.

For detailed metrics, see the report! 📖

---

## 🌍 Ethical Considerations

Aligned with [AI4People principles](https://doi.org/10.1007/s11023-018-9482-5):
- **Safety** 🔒: Robust battery management prevents operational failures.
- **Transparency** 📢: Clear bidding and reward criteria build trust.
- **Fairness** ⚖️: Decentralized allocation minimizes bias.

---

## 🔮 Future Work

- Optimize charger scheduling for AC strategy.
- Enhance Q-learning with epsilon-greedy or deep Q-networks.
- Improve code modularity for maintainability.

---

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🙌 Acknowledgments

- **Author**: Sepehr Mehregan, December 2024.
- **Tools**: Grok 3 assisted with summarizing references; Grammarly ensured clarity.
- **Dependencies**: NumPy, Pandas, Matplotlib.
- **Course**: Distributed Systems, December 2024.

⭐ **Star this repo** if you find it useful! Questions? Open an issue or reach out. Happy coding! 😄