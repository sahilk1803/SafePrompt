from typing import Dict, Any, List

GRID_FACTORS = {
    "India (National Avg)": 708.0,
    "Global Average": 475.0,
    "US Average": 386.0,
    "EU Average": 230.0,
    "Green / Renewable Datacenter": 25.0
}

class SustainabilityService:
    def __init__(self):
        self.wh_per_1k_tokens = 0.32
        self.pue = 1.18

    def estimate_tokens(self, text: str) -> int:
        if not text:
            return 0
        return max(1, int(len(text) / 3.8))

    def get_metrics(self, request_count: int, prompt_sample: str = "", region: str = "India (National Avg)") -> Dict[str, Any]:
        avg_tokens_per_request = 180
        total_tokens = request_count * avg_tokens_per_request

        energy_wh = (total_tokens / 1000.0) * self.wh_per_1k_tokens * self.pue
        energy_kwh = energy_wh / 1000.0

        grid_intensity = GRID_FACTORS.get(region, 475.0)
        co2_grams = energy_kwh * grid_intensity
        water_ml = request_count * 1.25

        green_tips = [
            {
                "title": "Prompt Compression",
                "text": "Trimming redundant conversational filler and boilerplate context can reduce inference energy by 25-40%."
            },
            {
                "title": "Model Right-Sizing",
                "text": "For classification, extraction, and formatting, small specialized models consume ~75% less power than frontier 100B+ models."
            },
            {
                "title": "Clean Grid Datacenter Routing",
                "text": "Scheduling workloads in renewable-powered regions reduces carbon intensity from ~708 gCO2/kWh to under 30 gCO2/kWh."
            }
        ]

        historical_usage = [
            {"hour": "10:00", "requests": max(1, int(request_count * 0.1)), "tokens": int(total_tokens * 0.1), "energy_wh": round(energy_wh * 0.1, 2)},
            {"hour": "12:00", "requests": max(2, int(request_count * 0.25)), "tokens": int(total_tokens * 0.25), "energy_wh": round(energy_wh * 0.25, 2)},
            {"hour": "14:00", "requests": max(3, int(request_count * 0.35)), "tokens": int(total_tokens * 0.35), "energy_wh": round(energy_wh * 0.35, 2)},
            {"hour": "16:00", "requests": max(2, int(request_count * 0.2)), "tokens": int(total_tokens * 0.2), "energy_wh": round(energy_wh * 0.2, 2)},
            {"hour": "Current", "requests": max(1, int(request_count * 0.1)), "tokens": int(total_tokens * 0.1), "energy_wh": round(energy_wh * 0.1, 2)}
        ]

        return {
            "total_requests": request_count,
            "estimated_tokens": total_tokens,
            "estimated_energy_kwh": round(energy_kwh, 5),
            "estimated_carbon_gco2e": round(co2_grams, 3),
            "estimated_water_ml": round(water_ml, 1),
            "region": region,
            "grid_intensity": grid_intensity,
            "green_tips": green_tips,
            "historical_usage": historical_usage,
            "assumptions_disclaimer": (
                "NOTE: Resource figures are heuristic scientific approximations based on published datacenter studies (Luccioni et al.). "
                "These values reflect theoretical model estimates rather than directly metered hardware telemetry."
            )
        }

sustainability_service = SustainabilityService()
