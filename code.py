import csv
import io
import pandas as pd

print("WELCOME TO DISASTER MANAGEMENT PROJECT")

class DataHandling:
    def __init__(self, file, year=None):   
        self.file = file
        self.year = year         

    def available_years(self):
        f = io.BytesIO(self.file) if isinstance(self.file, bytes) else self.file
        return sorted(pd.read_csv(f)["Year"].dropna().astype(int).unique().tolist())

    def load(self):
        return pd.DataFrame(self.file_data())

    def file_data(self):
        data = []        #creating an empty list to handle data
        
        lines = self.file.decode("utf-8").splitlines() if isinstance(self.file, bytes) else open(self.file, "r")
        reader = csv.DictReader(lines)

        for row in reader:           #reader is a pointe, which iterate over csv    
            self.csv_year = int(row["Year"])          #here csv_year is reads value by csv dynamically

            if self.year == self.csv_year:      #comparing year
                district_data = {
                    "district":  row["District"],
                    "population_affected" : row["Population_Affected"],
                    "village_damaged" : row["Villages_Damaged"],        
                    "crop_damage" : row["Crop_Area_Damaged_Hectares"],  
                    "human_deaths" : row["Human_Lives_Lost"],  
                    "relief_camps" : row["Relief_Camps_Opened"]
                }
                
                data.append(district_data)
        return data
                    
class PriorityCalculator():    
    def __init__(self, data):     
        self.data = data.to_dict("records") if isinstance(data, pd.DataFrame) else data
        
    def normalize(self):
        self.scaled_data = []

        for district in self.data:
            #minimum data
            min_pop_affected = min(self.data, key=lambda x: int(x["population_affected"]))["population_affected"]
            min_village_damaged = min(self.data, key=lambda x: int(x["village_damaged"]))["village_damaged"]
            min_crop_damaged = min(self.data, key=lambda x: float(x["crop_damage"]))["crop_damage"]
            min_human_deaths = min(self.data, key=lambda x: int(x["human_deaths"]))["human_deaths"]
            min_relief_camps = min(self.data, key=lambda x: int(x["relief_camps"]))["relief_camps"]

            # --- Maximum Values ---
            max_pop_affected = max(self.data, key=lambda x: int(x["population_affected"]))["population_affected"]
            max_village_damaged = max(self.data, key=lambda x: int(x["village_damaged"]))["village_damaged"]
            max_crop_damaged = max(self.data, key=lambda x: float(x["crop_damage"]))["crop_damage"]
            max_human_deaths = max(self.data, key=lambda x: int(x["human_deaths"]))["human_deaths"]
            max_relief_camps = max(self.data, key=lambda x: int(x["relief_camps"]))["relief_camps"]

        for district in self.data:
            pop_div = (int(max_pop_affected) - int(min_pop_affected)) or 1
            vil_div = (int(max_village_damaged) - int(min_village_damaged)) or 1
            crop_div = (float(max_crop_damaged) - float(min_crop_damaged)) or 1
            hum_div = (int(max_human_deaths) - int(min_human_deaths)) or 1
            rel_div = (int(max_relief_camps) - int(min_relief_camps)) or 1

            population_scaled = (int(district["population_affected"]) - int(min_pop_affected)) / pop_div
            village_scaled = (int(district["village_damaged"]) - int(min_village_damaged)) / vil_div
            crop_scaled = (float(district["crop_damage"])- float(min_crop_damaged)) / crop_div
            human_scaled = (int(district["human_deaths"]) - int(min_human_deaths)) / hum_div
            relief_scaled = (int(district["relief_camps"]) - int(min_relief_camps)) / rel_div

            obj = {
                "district": district["district"],
                "population_scaled" : population_scaled,
                "village_scaled" : village_scaled,
                "crop_scaled" : crop_scaled,
                "human_scaled" : human_scaled,
                "relief_scaled" : relief_scaled
            }
             
            self.scaled_data.append(obj)

    def score(self):
        score_data = []

        #calculating points for district
        for district in self.scaled_data:
            point_dist = (
                0.50 * district["human_scaled"]
                + 0.25 * district["population_scaled"]
                + 0.20 * district["village_scaled"]
                + 0.15 * district["crop_scaled"]
                + 0.25 * district["relief_scaled"]
            )

            score_data.append({
                "district": district["district"],
                "score": point_dist
            })

        # Highest score first
        score_data.sort(key=lambda x: x["score"], reverse=True)

        print("\nTOP 5 PRIORITY DISTRICTS")
        for district in score_data[:5]:
            print(f"{district['district']} -> {district['score']:.2f}")

        ranked_df = pd.DataFrame(self.data)
        score_map = {x["district"]: x["score"] for x in score_data}
        ranked_df["priority_score"] = ranked_df["district"].map(score_map)
        
        ranked_df = ranked_df.rename(columns={
            "district": "District",
            "human_deaths": "Human_Lives_Lost",
            "population_affected": "Population_Affected",
            "village_damaged": "Villages_Damaged"
        }).sort_values(by="priority_score", ascending=False)

        return ranked_df, sum(x["score"] for x in score_data)

if __name__ == "__main__":
    file = "flood_data.csv"
    year = int(input("Enter year: "))
    data_obj = DataHandling(file, year)

    if year not in range(2015, 2026):        
        raise Exception("Invalid year, please enter b/w 2015 - 2026")
    data = data_obj.load()

    cal_obj = PriorityCalculator(data)
    cal_obj.normalize()
    cal_obj.score()
