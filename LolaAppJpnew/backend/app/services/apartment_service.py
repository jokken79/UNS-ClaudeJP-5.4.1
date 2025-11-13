"""
Apartment Assignment Service

Intelligent apartment assignment with weighted scoring algorithm:
    - 40% Proximity to factory
    - 25% Availability
    - 15% Price affordability
    - 10% Roommate compatibility
    - 10% Transportation access
"""
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_
import math

from app.models.models import Apartment, Employee, Plant, Line, Company


# Scoring weights (must sum to 100)
WEIGHTS = {
    'proximity_to_factory': 40,
    'availability': 25,
    'price_affordability': 15,
    'roommate_compatibility': 10,
    'transportation': 10
}


class ApartmentService:
    """Service for intelligent apartment assignment"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_distance(
        self,
        lat1: Optional[float],
        lon1: Optional[float],
        lat2: Optional[float],
        lon2: Optional[float]
    ) -> float:
        """
        Calculate distance between two coordinates using Haversine formula

        Returns distance in kilometers
        """
        if not all([lat1, lon1, lat2, lon2]):
            return 999999.0  # Very large distance if coordinates missing

        # Earth radius in kilometers
        R = 6371.0

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    def score_proximity(self, apartment: Apartment, employee: Employee) -> float:
        """
        Score apartment proximity to employee's factory

        Returns score from 0.0 to 1.0 (1.0 = closest)
        """
        # Get employee's factory location
        line = self.db.query(Line).filter(Line.id == employee.line_id).first()
        if not line:
            return 0.0

        plant = self.db.query(Plant).filter(Plant.id == line.plant_id).first()
        if not plant:
            return 0.0

        # Calculate distance
        distance = self.calculate_distance(
            apartment.latitude,
            apartment.longitude,
            plant.latitude,
            plant.longitude
        )

        # Score based on distance (inverse relationship)
        # < 5km = 1.0, 5-10km = 0.8, 10-20km = 0.5, 20-30km = 0.3, >30km = 0.1
        if distance < 5:
            return 1.0
        elif distance < 10:
            return 0.8
        elif distance < 20:
            return 0.5
        elif distance < 30:
            return 0.3
        else:
            return 0.1

    def score_availability(self, apartment: Apartment) -> float:
        """
        Score apartment availability

        Returns score from 0.0 to 1.0 (1.0 = most available)
        """
        if not apartment.is_available:
            return 0.0

        if apartment.total_capacity == 0:
            return 0.0

        # Calculate occupancy rate
        occupancy_rate = apartment.current_occupancy / apartment.total_capacity

        # Score based on availability (inverse of occupancy)
        # 0% occupancy = 1.0, 50% = 0.5, 100% = 0.0
        return max(0.0, 1.0 - occupancy_rate)

    def score_price(self, apartment: Apartment, employee: Employee) -> float:
        """
        Score apartment price affordability

        Returns score from 0.0 to 1.0 (1.0 = most affordable)
        """
        # Calculate rent as percentage of monthly salary
        # Assuming 160 hours/month work
        monthly_salary = employee.jikyu * 160

        if monthly_salary == 0:
            return 0.0

        rent_ratio = apartment.monthly_rent / monthly_salary

        # Score based on rent ratio
        # < 20% = 1.0, 20-30% = 0.7, 30-40% = 0.4, >40% = 0.1
        if rent_ratio < 0.20:
            return 1.0
        elif rent_ratio < 0.30:
            return 0.7
        elif rent_ratio < 0.40:
            return 0.4
        else:
            return 0.1

    def score_compatibility(self, apartment: Apartment, employee: Employee) -> float:
        """
        Score roommate compatibility

        Considers gender, nationality, age
        Returns score from 0.0 to 1.0
        """
        # Get current residents
        residents = self.db.query(Employee).filter(
            and_(
                Employee.apartment_id == apartment.id,
                Employee.status == 'ACTIVE'
            )
        ).all()

        if not residents:
            return 1.0  # Empty apartment, full compatibility

        # Score based on compatibility factors
        compatibility_score = 0.0
        factor_count = 0

        # Gender compatibility (same gender = 1.0, mixed = 0.5)
        same_gender_count = sum(1 for r in residents if r.gender == employee.gender)
        gender_ratio = same_gender_count / len(residents)
        compatibility_score += gender_ratio
        factor_count += 1

        # Nationality compatibility (same nationality = bonus)
        same_nationality_count = sum(1 for r in residents if r.nationality == employee.nationality)
        nationality_ratio = same_nationality_count / len(residents)
        compatibility_score += nationality_ratio * 0.5  # 50% weight
        factor_count += 0.5

        # Age compatibility (within 10 years = good)
        if employee.date_of_birth:
            from datetime import date
            employee_age = (date.today() - employee.date_of_birth).days // 365

            age_compatible_count = 0
            for resident in residents:
                if resident.date_of_birth:
                    resident_age = (date.today() - resident.date_of_birth).days // 365
                    if abs(employee_age - resident_age) <= 10:
                        age_compatible_count += 1

            age_ratio = age_compatible_count / len(residents) if residents else 0
            compatibility_score += age_ratio * 0.5  # 50% weight
            factor_count += 0.5

        # Normalize score
        return compatibility_score / factor_count if factor_count > 0 else 0.5

    def score_transportation(self, apartment: Apartment, employee: Employee) -> float:
        """
        Score transportation access

        Placeholder - would require transit API integration
        Returns score from 0.0 to 1.0
        """
        # For now, use distance as proxy
        # In production, would use Google Maps API or similar
        line = self.db.query(Line).filter(Line.id == employee.line_id).first()
        if not line:
            return 0.5

        plant = self.db.query(Plant).filter(Plant.id == line.plant_id).first()
        if not plant:
            return 0.5

        distance = self.calculate_distance(
            apartment.latitude,
            apartment.longitude,
            plant.latitude,
            plant.longitude
        )

        # Simple scoring based on distance
        if distance < 2:
            return 1.0  # Walking distance
        elif distance < 10:
            return 0.8  # Good public transit
        elif distance < 20:
            return 0.5  # Moderate commute
        else:
            return 0.3  # Long commute

    def calculate_apartment_score(
        self,
        apartment: Apartment,
        employee: Employee
    ) -> Tuple[float, Dict[str, float]]:
        """
        Calculate total weighted score for apartment-employee match

        Returns (total_score, individual_scores)
        """
        scores = {
            'proximity': self.score_proximity(apartment, employee),
            'availability': self.score_availability(apartment),
            'price': self.score_price(apartment, employee),
            'compatibility': self.score_compatibility(apartment, employee),
            'transportation': self.score_transportation(apartment, employee)
        }

        # Calculate weighted total
        total_score = (
            scores['proximity'] * WEIGHTS['proximity_to_factory'] +
            scores['availability'] * WEIGHTS['availability'] +
            scores['price'] * WEIGHTS['price_affordability'] +
            scores['compatibility'] * WEIGHTS['roommate_compatibility'] +
            scores['transportation'] * WEIGHTS['transportation']
        ) / 100.0

        return total_score, scores

    def recommend_apartments(
        self,
        employee: Employee,
        max_results: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Recommend apartments for employee using weighted scoring

        Returns list of apartments with scores, sorted by best match
        """
        # Get all available apartments
        apartments = self.db.query(Apartment).filter(
            Apartment.is_available == True,
            Apartment.is_deleted == False,
            Apartment.current_occupancy < Apartment.total_capacity
        ).all()

        # Calculate scores for each apartment
        recommendations = []
        for apartment in apartments:
            total_score, individual_scores = self.calculate_apartment_score(apartment, employee)

            recommendations.append({
                'apartment': apartment,
                'total_score': total_score,
                'scores': individual_scores,
                'monthly_rent': apartment.monthly_rent,
                'available_capacity': apartment.total_capacity - apartment.current_occupancy,
                'amenities': apartment.amenities
            })

        # Sort by total score (descending)
        recommendations.sort(key=lambda x: x['total_score'], reverse=True)

        # Return top N results
        return recommendations[:max_results]

    def assign_apartment(
        self,
        employee: Employee,
        apartment: Apartment,
        move_in_date: str
    ) -> bool:
        """
        Assign employee to apartment

        Updates employee record and apartment occupancy
        """
        from app.models.models import ApartmentAssignment
        from datetime import datetime

        # Check capacity
        if apartment.current_occupancy >= apartment.total_capacity:
            raise ValueError("Apartment is at full capacity")

        # Create assignment record
        assignment = ApartmentAssignment(
            employee_id=employee.hakenmoto_id,
            apartment_id=apartment.id,
            move_in_date=datetime.strptime(move_in_date, "%Y-%m-%d").date(),
            monthly_rent=apartment.monthly_rent,
            is_active=True
        )

        self.db.add(assignment)

        # Update employee
        employee.apartment_id = apartment.id

        # Update apartment occupancy
        apartment.current_occupancy += 1

        self.db.commit()

        return True

    def suggest_transfer(
        self,
        employee: Employee
    ) -> Optional[Dict[str, Any]]:
        """
        Suggest apartment transfer if better option available

        Returns suggestion if found, None otherwise
        """
        if not employee.apartment_id:
            return None

        current_apartment = self.db.query(Apartment).filter(
            Apartment.id == employee.apartment_id
        ).first()

        if not current_apartment:
            return None

        # Calculate current score
        current_score, _ = self.calculate_apartment_score(current_apartment, employee)

        # Get recommendations
        recommendations = self.recommend_apartments(employee, max_results=1)

        if not recommendations:
            return None

        best_recommendation = recommendations[0]
        best_score = best_recommendation['total_score']

        # Suggest transfer if improvement is significant (>20%)
        if best_score > current_score * 1.2:
            return {
                'current_apartment': current_apartment,
                'current_score': current_score,
                'suggested_apartment': best_recommendation['apartment'],
                'suggested_score': best_score,
                'improvement': ((best_score - current_score) / current_score) * 100
            }

        return None
