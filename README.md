# StatsBomb Passing Network & Match Analysis Tool

A Python-based football analytics and scouting tool that fetches open-source match data from StatsBomb, calculates player average positions, visualizes tactical passing networks, and generates detailed match squad breakdowns with substitution tracking.

## Features
- **Interactive Menu**: Explore all available StatsBomb competitions/leagues and list matches with their respective Match IDs dynamically.
- **Passing Network Visualization**: Plots tactical passing networks on a standard StatsBomb pitch using `mplsoccer` and `matplotlib`, styled with a modern dark theme.
- **Node & Color Differentiation**: 
  - Starting XI players are represented with **Pink** nodes.
  - Substitutes who played are represented with **Yellow** nodes.
- **Advanced Substitution Tracking**: Automatically detects substitution events and lists player minute markers (`<- [minute]` for players going off, `-> [minute]` for substitutes coming on) in a clean match squad panel.
- **Node Sizing & Jersey Numbers**: Dynamic node scaling based on pass counts, displaying official squad jersey numbers on each node.

## Prerequisites & Installation

Make sure you have Python installed, then install the required dependencies:

```bash
pip install matplotlib numpy pandas mplsoccer statsbombpy