from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tariff import Tariff

class TariffService:
    @staticmethod
    async def calculate_water_amount(db: AsyncSession, customer_type: str, consumption: float) -> float:
        """
        Tính tiền nước dựa trên bậc thang cấu hình trong DB.
        """
        stmt = select(Tariff).where(Tariff.customer_type == customer_type).order_by(Tariff.step_number)
        result = await db.execute(stmt)
        tariffs = result.scalars().all()
        
        if not tariffs:
            # Fallback nếu chưa cấu hình DB
            return consumption * 10000 
            
        total_amount = 0
        remaining_consumption = consumption
        
        for tariff in tariffs:
            if remaining_consumption <= 0:
                break
                
            # Tính số khối trong bậc này
            step_limit = (tariff.to_m3 - tariff.from_m3) if tariff.to_m3 else float('inf')
            m3_in_this_step = min(remaining_consumption, step_limit)
            
            total_amount += m3_in_this_step * tariff.price_per_m3
            remaining_consumption -= m3_in_this_step
            
        return total_amount

    @staticmethod
    def get_full_bill_details(water_amount: float, previous_debt: float = 0):
        vat = water_amount * 0.05
        env_fee = water_amount * 0.10
        total = water_amount + vat + env_fee + previous_debt
        return {
            "water_amount": water_amount,
            "vat_amount": vat,
            "env_fee_amount": env_fee,
            "previous_debt": previous_debt,
            "total_amount": total
        }
