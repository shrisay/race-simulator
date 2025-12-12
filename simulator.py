import random
import time
#random.seed(41)

class Track:
    def __init__(self, name, cornering_boost, overtake_boost):   #Cornering boost is a number from 1 to 99. 50 is a track that equally weights car speed and cornering
        self.name = name
        self.corner_effect = cornering_boost
        self.overtake = overtake_boost


class Car:
    def __init__(self, name, speed, cornering, reliability):
        self.name = name
        self.speed = speed
        self.cornering = cornering
        self.reliability = reliability


class Driver:
    def __init__(self, name, pace, awareness, racecraft, consistency, car: Car, grid_penalty = 0):
        self.name = name
        self.pace = pace
        self.pace_buff = 0
        self.awareness = awareness
        self.racecraft = racecraft
        self.consistency = consistency
        self.car = car
        self.total_time = 0.0
        self.gap_to_leader = 0.0
        self.current_lap_time = 0.0

        if grid_penalty == 5:
            self.pace_buff = 2
        elif grid_penalty == 10:
            self.pace_buff = 4

        self.grid_penalty = grid_penalty 

    def simulate_lap(self, track: Track):
        messages = []

        pace_factor = 12.5 + (self.pace+self.pace_buff)*0.125
        car_factor = (self.car.cornering*track.corner_effect + self.car.speed*(100-track.corner_effect))/100*0.25

        # Consistency adds randomness
        inconsistency = (100 - self.consistency) / 10
        random_factor = random.uniform(-(inconsistency+0.2), 0)  # A perfect driver will vary by 0.2s per lap

        # Reliability issue
        if random.random() < (100 - self.car.reliability) / 1500:
            reliability_penalty = random.uniform(7, 10)
            messages.append(f"{self.name} had a car issue!")
        else:
            reliability_penalty = 0

        # Driver error
        driver_error_chance = (100 - self.consistency) / 200
        if random.random() < driver_error_chance:
            mistake_penalty = random.uniform(1.5, 4)  
            messages.append(f"{self.name} made a mistake!")
        else:
            mistake_penalty = 0

        lap_factor = pace_factor + car_factor + random_factor - reliability_penalty - mistake_penalty
        lap_time = 130 - lap_factor

        self.current_lap_time = lap_time
        self.total_time += lap_time
        return [messages, self.current_lap_time]



# === RACE SIM ===

class Race:
    def __init__(self, drivers, num_laps, track: Track):
        self.drivers = drivers
        self.num_laps = num_laps
        self.track = track
        self.fastest_lap = float('inf')
        self.fastest_driver = ""
        self.fastest_lap_no = 0
        
    def qualify(self):
        print(f"🏁 Qualifying Session 🏁 - {self.track.name}")
        
        qualifying_times = []
        
        for driver in self.drivers:
            pace_factor = 21 + driver.pace * 0.17
            car_factor = (driver.car.cornering * self.track.corner_effect + 
                        driver.car.speed * (100 - self.track.corner_effect)) / 100 * 0.34
            
            # Qualifying has more inconsistency but quicker laps
            inconsistency = (100 - driver.consistency) / 8
            random_factor = random.uniform(-(inconsistency+0.2), 0) # A perfect driver will vary by 0.2s per lap
            
            # Very low risk of car issue
            if random.random() < (100 - driver.car.reliability) / 3000:  
                reliability_penalty = random.uniform(2, 4)
            else:
                reliability_penalty = 0
            
            lap_factor = pace_factor + car_factor + random_factor - reliability_penalty
            lap_time = 150 - lap_factor
            
            qualifying_times.append((driver, lap_time))
        
        # Sort by time (fastest first)
        qualifying_times.sort(key=lambda x: x[1])
        
        # Display qualifying results
        print("=== QUALIFYING RESULTS ===")
        for pos, (driver, time) in enumerate(qualifying_times, start=1):
            gap = time - qualifying_times[0][1]
            penalty_text = f" (+{driver.grid_penalty} penalty)" if driver.grid_penalty > 0 else ""
            print(f"{pos}. {driver.name:<12} | {driver.car.name:<10} | {time:.3f}s | +{gap:.3f}s | {penalty_text}")

        print()

        # Create starting grid
        print("=== STARTING GRID ===")
        race_grid = [driver for driver, time in qualifying_times]

        for driver in race_grid[:]:  
            if driver.grid_penalty > 0:
                current_pos = race_grid.index(driver)
                race_grid.remove(driver)
                new_pos = min(current_pos + driver.grid_penalty, len(race_grid))
                race_grid.insert(new_pos, driver)

        for pos, driver in enumerate(race_grid, start=1):
            print(f"{pos}. {driver.name:<12} | {driver.car.name:<10}")

        print()

        # Update driver order for race
        self.drivers = race_grid
        print()
        
        # Return polesitter name
        return qualifying_times[0][0].name
    
    def simulate(self):
        print(f"🏁 Race Start! 🏁 - {self.track.name}")
        time.sleep(0.6)

        # Start order = as given
        order = self.drivers.copy()

        for i, driver in enumerate(order):
            driver.total_time = i * 0.5 

        # Simulate a lap
        for lap in range(1, self.num_laps + 1):
            print(f"--- Lap {lap} ---")

            messages = []

            # simulate lap times
            for driver in order:
                info = driver.simulate_lap(self.track)
                issue_messages = info[0]
                for message in issue_messages:
                    print(message)
                
                laptime = info[1]
                if laptime < self.fastest_lap:
                    self.fastest_lap = laptime
                    self.fastest_driver = driver.name
                    self.fastest_lap_no = lap

            # Check overtakes with multiple passes
            # Keep checking until no more overtakes happen in this lap
            overtakes_occurred = True

            while overtakes_occurred:
                overtakes_occurred = False
                
                # Check from FRONT to BACK
                for i in range(1, len(order)):
                    behind = order[i]
                    ahead = order[i - 1]

                    new_gap = behind.total_time - ahead.total_time

                    if new_gap < -1.5:
                        order[i - 1], order[i] = order[i], order[i - 1]
                        messages.append(f"{order[i - 1].name} flew past {order[i].name}!")
                        overtakes_occurred = True

                    elif new_gap < 0.15:
                        overtake_chance = (
                            (behind.racecraft - ahead.awareness) / 200
                            + (behind.car.speed - ahead.car.speed)*(100 - self.track.corner_effect) / 40000
                            + (behind.car.cornering - ahead.car.cornering)*self.track.corner_effect / 40000
                        )
                        
                        overtake_probability = (max(0, min(1, 0.45 + overtake_chance * 7))) * self.track.overtake/100
                        
                        if random.random() < overtake_probability:
                            order[i - 1], order[i] = order[i], order[i - 1]
                            order[i - 1].total_time += random.uniform(0.5, 1)
                            order[i].total_time = order[i - 1].total_time + random.uniform(0.15, 0.4)
                            messages.append(f"{order[i - 1].name} overtook {order[i].name}!")
                            overtakes_occurred = True

                        else:
                            ahead.total_time += random.uniform(0.15, 0.4)
                            behind.total_time = ahead.total_time + random.uniform(0.15, 0.3)
                            messages.append(f"{ahead.name} held off {behind.name}.")

            # Update gaps
            leader_time = min(d.total_time for d in order)
            for driver in order:
                driver.gap_to_leader = driver.total_time - leader_time


            # Display current standings
            for pos, d in enumerate(order, start=1):
                print(f" {pos}. {d.name:<12} | Car: {d.car.name:<10} | Gap: +{d.gap_to_leader:.2f}s")
            for message in messages:
                print(message)

            print()
            time.sleep(0.7)

        # Final results
        print(f"\n=== FINAL RESULTS - {self.track.name} ===")
        for pos, d in enumerate(order, start=1):
            print(f"{pos}. {d.name:<12} | {d.car.name:<10} | Total: {d.total_time:.2f}s")
        print(f"Fastest lap ⏰ - {self.fastest_driver} : {self.fastest_lap:.3f}s | Lap {self.fastest_lap_no}")

        print("\n🏁 Race Finished 🏁")

mercedes = Car("Mercedes", 93, 95, 98)  #SPEED, CORNERING, RELIABILITY
redbull = Car("Red Bull", 97, 92, 91)
mclaren = Car("McLaren", 96, 97, 95)
ferrari = Car("Ferrari", 95, 92, 88)
aston = Car("AMR", 93, 88, 87)
alpine = Car("Alpine", 89, 92, 84)
haas = Car("Haas", 89, 91, 89)
williams = Car("Williams", 92, 89, 91)

#PAC, AWA, RAC, CONSISTENCY
drivers = [
    Driver("Perez", 92, 95, 86, 88, redbull),
    Driver("Russell", 93.5, 95, 93, 94, mercedes),
    Driver("Leclerc", 94, 97, 95, 96, ferrari),
    Driver("Verstappen", 95, 95, 96, 97, redbull),
    Driver("Hamilton", 94, 91, 98, 96, mercedes),
    Driver("Norris", 93, 89, 91, 90, mclaren),
    Driver("Piastri", 92, 93, 96, 93, mclaren),
    Driver("Sainz", 92, 89, 94, 93, ferrari),
    Driver("Alonso", 89, 97, 95, 93, alpine),
    Driver("Vettel", 91, 96, 92, 95, aston),
    Driver("Stroll", 85, 83, 84, 86, aston),
    Driver("Ocon", 87, 89, 91, 89, alpine),
    Driver("Bearman", 88, 96, 91, 90, haas),
    Driver("Magnussen", 85, 98, 90, 90, haas),
    Driver("Albon", 91, 90, 90, 92, williams),
    Driver("Bottas", 92, 90, 91, 92, williams)
]

spa = Track("Spa-Francorchamps", 48, 85)
monza = Track("Monza", 30, 90)
mexico = Track("Mexico City", 67, 75)
monaco = Track("Monaco", 83, 27)
bahrain = Track("Bahrain", 43, 94)
silverstone = Track("Silverstone", 58, 82)
australia = Track("Australia", 41, 80)
singapore = Track("Singapore", 72, 53)

race = Race(drivers, 45, silverstone)
race.qualify()
race.simulate()