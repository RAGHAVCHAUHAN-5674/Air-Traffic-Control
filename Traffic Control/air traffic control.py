import math
import random
import heapq
import csv
from dataclasses import dataclass
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import Button
@dataclass
class Airport:
    name: str
    x: float
    y: float
    capacity: int
    current_traffic: int = 0
@dataclass
class Aircraft:
    flight_id: str
    source: str
    destination: str
    route: list
    current_node: str
    next_node: str
    progress: float
    speed: float
    fuel: float
    delay: float
    status: str
    completed: bool = False
class AirTrafficControl:
    def __init__(self):
        self.airports = {}
        self.distances = {}
        self.mst_edges = []
        self.aircraft = []
        self.time = 0
        self.total_distance = 0
        self.total_delay = 0
        self.total_fuel = 0
        self.conflicts = 0
        self.completed_flights = 0
        self.simulation_running = True
        self.create_airports()
        self.create_distance_matrix()
        self.calculate_mst()
        self.generate_aircraft(12)
    def create_airports(self):
        airport_data = [
            ("DEL", 20, 80, 5),
            ("BOM", 20, 25, 5),
            ("BLR", 50, 20, 4),
            ("HYD", 55, 45, 4),
            ("MAA", 75, 15, 4),
            ("CCU", 80, 75, 4),
            ("AMD", 10, 55, 3),
            ("JAI", 30, 65, 3),
            ("LKO", 45, 85, 3),
            ("GOI", 35, 10, 3)
        ]
        for name, x, y, capacity in airport_data:
            self.airports[name] = Airport(
                name,
                x,
                y,
                capacity
            )
    def create_distance_matrix(self):
        names = list(self.airports.keys())
        for a in names:
            self.distances[a] = {}
            for b in names:
                if a == b:
                    self.distances[a][b] = 0
                else:
                    x1 = self.airports[a].x
                    y1 = self.airports[a].y
                    x2 = self.airports[b].x
                    y2 = self.airports[b].y
                    distance = math.sqrt(
                        (x2 - x1) ** 2 +
                        (y2 - y1) ** 2
                    )
                    self.distances[a][b] = distance
    def calculate_mst(self):
        """
        Prim's algorithm finds a Minimum Spanning Tree.
        The airport network is represented as a weighted
        graph where:
        Node   = Airport
        Edge   = Air route
        Weight = Distance between airports
        """
        names = list(self.airports.keys())
        if not names:
            return
        visited = set()
        min_heap = []
        start = names[0]
        visited.add(start)
        for destination in names:
            if destination != start:
                weight = self.distances[start][destination]
                heapq.heappush(
                    min_heap,
                    (weight, start, destination)
                )
        self.mst_edges = []
        while min_heap and len(visited) < len(names):
            weight, source, destination = heapq.heappop(
                min_heap
            )
            if destination in visited:
                continue
            visited.add(destination)
            self.mst_edges.append(
                (source, destination, weight)
            )
            for next_node in names:
                if next_node not in visited:
                    next_weight = self.distances[
                        destination
                    ][next_node]
                    heapq.heappush(
                        min_heap,
                        (
                            next_weight,
                            destination,
                            next_node
                        )
                    )
    def display_mst(self):
        print("\n============================================")
        print("MINIMUM SPANNING TREE - PRIM'S ALGORITHM")
        print("============================================")
        total = 0
        for source, destination, weight in self.mst_edges:
            print(
                f"{source} ---- {destination} "
                f"Distance = {weight:.2f}"
            )
            total += weight
        print("--------------------------------------------")
        print(f"Total MST Distance: {total:.2f}")
        print("============================================")
    def find_route(self, source, destination):
        """
        Find route between two airports using
        the Minimum Spanning Tree.
        Since MST is a tree, there is exactly one
        path between two nodes.
        """
        graph = {
            airport: []
            for airport in self.airports
        }

        for a, b, weight in self.mst_edges:

            graph[a].append((b, weight))
            graph[b].append((a, weight))

        queue = [(source, [source])]

        visited = set()

        while queue:

            current, path = queue.pop(0)

            if current == destination:

                return path

            if current in visited:

                continue

            visited.add(current)

            for neighbor, weight in graph[current]:

                if neighbor not in visited:

                    queue.append(
                        (
                            neighbor,
                            path + [neighbor]
                        )
                    )

        return []


    # =====================================================
    # 9. GENERATE AIRCRAFT
    # =====================================================

    def generate_aircraft(self, number):

        airport_names = list(self.airports.keys())

        for i in range(number):

            source, destination = random.sample(
                airport_names,
                2
            )

            route = self.find_route(
                source,
                destination
            )

            if len(route) < 2:
                continue

            flight = Aircraft(

                flight_id=f"AI-{100+i}",

                source=source,

                destination=destination,

                route=route,

                current_node=route[0],

                next_node=route[1],

                progress=0,

                speed=random.uniform(
                    0.015,
                    0.035
                ),

                fuel=random.uniform(
                    80,
                    100
                ),

                delay=0,

                status="Flying"

            )

            self.aircraft.append(flight)

            self.airports[source].current_traffic += 1


    # =====================================================
    # 10. DISTANCE FUNCTION
    # =====================================================

    def distance_between(self, a, b):

        return self.distances[a][b]


    # =====================================================
    # 11. UPDATE AIRCRAFT
    # =====================================================

    def update_aircraft(self):

        for flight in self.aircraft:

            if flight.completed:
                continue

            # ------------------------------------------------
            # AIRPORT CAPACITY CHECK
            # ------------------------------------------------

            airport = self.airports[
                flight.next_node
            ]

            if airport.current_traffic >= airport.capacity:

                flight.status = "Holding"

                flight.delay += 1

                self.total_delay += 1

                continue

            else:

                flight.status = "Flying"


            # ------------------------------------------------
            # MOVE AIRCRAFT
            # ------------------------------------------------

            flight.progress += flight.speed

            # Fuel consumption

            flight.fuel -= (
                flight.speed * 1.8
            )

            self.total_fuel += (
                flight.speed * 1.8
            )

            # ------------------------------------------------
            # AIRCRAFT REACHES NEXT AIRPORT
            # ------------------------------------------------

            if flight.progress >= 1:

                flight.progress = 0

                previous = flight.current_node

                flight.current_node = flight.next_node

                current_index = flight.route.index(
                    flight.current_node
                )

                # Decrease traffic at previous airport

                if self.airports[
                    previous
                ].current_traffic > 0:

                    self.airports[
                        previous
                    ].current_traffic -= 1

                # Check destination

                if (
                    flight.current_node
                    == flight.destination
                ):

                    flight.completed = True

                    flight.status = "Landed"

                    self.completed_flights += 1

                    continue

                # Move to next node

                if (
                    current_index + 1
                    < len(flight.route)
                ):

                    flight.next_node = (
                        flight.route[
                            current_index + 1
                        ]
                    )

                    self.airports[
                        flight.current_node
                    ].current_traffic += 1


    # =====================================================
    # 12. GET AIRCRAFT POSITION
    # =====================================================

    def get_aircraft_position(self, flight):

        if flight.completed:

            airport = self.airports[
                flight.destination
            ]

            return airport.x, airport.y

        current = self.airports[
            flight.current_node
        ]

        next_airport = self.airports[
            flight.next_node
        ]

        x = (
            current.x +
            (
                next_airport.x -
                current.x
            ) *
            flight.progress
        )

        y = (
            current.y +
            (
                next_airport.y -
                current.y
            ) *
            flight.progress
        )

        return x, y


    # =====================================================
    # 13. SAFETY CONFLICT DETECTION
    # =====================================================

    def detect_conflicts(self):

        positions = []

        for flight in self.aircraft:

            if flight.completed:
                continue

            x, y = self.get_aircraft_position(
                flight
            )

            positions.append(
                (
                    flight.flight_id,
                    x,
                    y
                )
            )

        conflicts_this_step = 0

        for i in range(len(positions)):

            for j in range(i + 1, len(positions)):

                id1, x1, y1 = positions[i]

                id2, x2, y2 = positions[j]

                distance = math.sqrt(
                    (x2 - x1) ** 2 +
                    (y2 - y1) ** 2
                )

                # Minimum safe separation

                if distance < 4:

                    conflicts_this_step += 1

        self.conflicts += conflicts_this_step

        return conflicts_this_step


    # =====================================================
    # 14. CALCULATE TRAFFIC STATISTICS
    # =====================================================

    def statistics(self):

        total_flights = len(
            self.aircraft
        )

        completed = self.completed_flights

        average_delay = (
            self.total_delay /
            total_flights
            if total_flights > 0
            else 0
        )

        active = sum(
            not f.completed
            for f in self.aircraft
        )

        return {

            "Total Flights":
                total_flights,

            "Completed Flights":
                completed,

            "Active Flights":
                active,

            "Total Delay":
                self.total_delay,

            "Average Delay":
                average_delay,

            "Safety Conflicts":
                self.conflicts,

            "Fuel Consumed":
                self.total_fuel

        }


    # =====================================================
    # 15. SAVE REPORT
    # =====================================================

    def save_report(self):

        data = []

        for flight in self.aircraft:

            data.append({

                "Flight ID":
                    flight.flight_id,

                "Source":
                    flight.source,

                "Destination":
                    flight.destination,

                "Route":
                    " -> ".join(
                        flight.route
                    ),

                "Delay":
                    round(
                        flight.delay,
                        2
                    ),

                "Fuel Used":
                    round(
                        100 - flight.fuel,
                        2
                    ),

                "Status":
                    flight.status

            })

        df = pd.DataFrame(data)

        df.to_csv(
            "air_traffic_report.csv",
            index=False
        )

        print(
            "\nReport saved as "
            "'air_traffic_report.csv'"
        )


# =========================================================
# 16. VISUALIZATION CLASS
# =========================================================

class TrafficVisualization:

    def __init__(self, system):

        self.system = system

        self.fig, self.ax = plt.subplots(
            figsize=(13, 8)
        )

        plt.subplots_adjust(
            bottom=0.18
        )

        self.ax.set_title(
            "AIR TRAFFIC CONTROL SYSTEM",
            fontsize=18,
            fontweight="bold"
        )

        self.ax.set_xlabel(
            "Airspace X Coordinate"
        )

        self.ax.set_ylabel(
            "Airspace Y Coordinate"
        )

        self.ax.grid(
            True,
            linestyle="--",
            alpha=0.4
        )

        self.ax.set_xlim(
            0,
            90
        )

        self.ax.set_ylim(
            0,
            95
        )

        self.draw_network()

        self.create_buttons()


    # =====================================================
    # 17. DRAW AIRPORT NETWORK
    # =====================================================

    def draw_network(self):

        # Draw all possible routes lightly

        names = list(
            self.system.airports.keys()
        )

        for i in range(len(names)):

            for j in range(i + 1, len(names)):

                a = self.system.airports[
                    names[i]
                ]

                b = self.system.airports[
                    names[j]
                ]

                self.ax.plot(

                    [a.x, b.x],

                    [a.y, b.y],

                    linestyle=":",

                    alpha=0.15

                )


        # Draw MST

        for source, destination, weight in self.system.mst_edges:

            a = self.system.airports[
                source
            ]

            b = self.system.airports[
                destination
            ]

            self.ax.plot(

                [a.x, b.x],

                [a.y, b.y],

                linewidth=3,

                alpha=0.7

            )


        # Draw airports

        for name, airport in self.system.airports.items():

            self.ax.scatter(

                airport.x,

                airport.y,

                s=180,

                marker="^"

            )

            self.ax.text(

                airport.x + 1,

                airport.y + 1,

                name,

                fontsize=10,

                fontweight="bold"

            )
    def create_buttons(self):

        ax_start = plt.axes(
            [0.12, 0.04, 0.15, 0.06]
        )
        ax_report = plt.axes(
            [0.32, 0.04, 0.15, 0.06]
        )
        ax_exit = plt.axes(
            [0.52, 0.04, 0.15, 0.06]
        )
        self.start_button = Button(
            ax_start,
            "Start / Pause"
        )
        self.report_button = Button(
            ax_report,
            "Save Report"
        )
        self.exit_button = Button(
            ax_exit,
            "Exit"
        )
        self.start_button.on_clicked(
            self.toggle_simulation
        )
        self.report_button.on_clicked(
            self.save_report
        )
        self.exit_button.on_clicked(
            self.close_program
        )
    def toggle_simulation(self, event):

        self.system.simulation_running = (
            not self.system.simulation_running
        )
    def save_report(self, event):
        self.system.save_report()
    def close_program(self, event):
        plt.close(
            self.fig
        )
    def update(self, frame):
        if self.system.simulation_running:
            self.system.time += 1
            self.system.update_aircraft()
            conflicts = (
                self.system.detect_conflicts()
            )
        else:
            conflicts = 0
        self.ax.clear()
        self.ax.set_xlim(
            0,
            90
        )
        self.ax.set_ylim(
            0,
            95
        )
        self.ax.set_xlabel(
            "Airspace X Coordinate"
        )
        self.ax.set_ylabel(
            "Airspace Y Coordinate"
        )
        self.ax.grid(
            True,
            linestyle="--",
            alpha=0.4
        )
        self.draw_network()
        for flight in self.system.aircraft:
            if flight.completed:
                continue
            x, y = (
                self.system
                .get_aircraft_position(
                    flight
                )
            )
            self.ax.scatter(
                x,
                y,
                s=100,
                marker="o"
            )
            self.ax.text(
                x + 1,
                y + 1,
                flight.flight_id,
                fontsize=8
            )
        stats = (
            self.system
            .statistics()
        )
        title = (
            "AIR TRAFFIC CONTROL SYSTEM\n"
            f"Simulation Time: "
            f"{self.system.time} | "
            f"Flights: "
            f"{stats['Total Flights']} | "
            f"Completed: "
            f"{stats['Completed Flights']} | "
            f"Delay: "
            f"{stats['Total Delay']} | "
            f"Conflicts: "
            f"{stats['Safety Conflicts']}"
        )
        self.ax.set_title(
            title,
            fontsize=14,
            fontweight="bold"
        )
def main():
    print("\n")
    print("=" * 60)
    print("       AIR TRAFFIC CONTROL SIMULATION")
    print("=" * 60)
    print("\nInitializing airports...")
    system = AirTrafficControl()
    print(
        f"Total Airports: "
        f"{len(system.airports)}"
    )
    print(
        f"Total Aircraft: "
        f"{len(system.aircraft)}"
    )
    system.display_mst()
    print("\nAirport Information")
    print("-" * 60)
    for airport in system.airports.values():
        print(
            f"{airport.name:<5} "
            f"Capacity: "
            f"{airport.capacity}"
        )
    print("\nStarting simulation...")
    visualization = TrafficVisualization(
        system
    )
    animation = FuncAnimation(
        visualization.fig,
        visualization.update,
        interval=100,
        cache_frame_data=False
    )
    plt.show()
    system.save_report()
    print("\nFinal Performance Analysis")
    print("=" * 60)
    statistics = system.statistics()
    for key, value in statistics.items():
        print(
            f"{key:<25}: "
            f"{value}"
        )
    print("=" * 60)
if __name__ == "__main__":
    main()