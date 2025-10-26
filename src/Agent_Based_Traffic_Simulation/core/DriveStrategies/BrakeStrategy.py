import numpy as np
from .AbstractDriveStrategy import AbstractDriveStrategy
from ..Utils import change_magnitude, EPS, to_unit

class BrakeStrategy(AbstractDriveStrategy):
    name = "brake"
    
    
    def big_brake(self, traffic_agent, v_lead, v_now, lead, b_hard, a_safety):

        kv        = 0.12     # ms^-1, speed tracking gain
        b_margin  = 0.05     # mm/ms^2, extra over leader braking

        v_tar     = 0.75 * v_lead
        a_track   = - kv * (v_now - v_tar)   # mm/ms^2

        # Signed longitudinal leader acceleration (mm/ms^2)
        # Use leader velocity direction. Fall back to follower direction if leader is nearly stopped.
        lead_dir  = to_unit(lead.vehicle.velocity) if np.linalg.norm(lead.vehicle.velocity) > EPS else to_unit(traffic_agent.vehicle.velocity)
        aL_long   = float(np.dot(lead.vehicle.acceleration, lead_dir))

        # a_emerg = max(-b_hard, min(aL_long - b_margin, a_track))
        a_emerg   = max(-b_hard, min(aL_long - b_margin, a_track))

        # Take the stronger braking between your normal command and the emergency rule
        return min(a_safety, a_emerg)

    def step(self, traffic_agent):
        dt = float(traffic_agent.model.dt)  # ms

        lead = traffic_agent.lead
        gap_mm = traffic_agent.gap_to_lead  # bumper-to-bumper gap from your find_lead_and_gap
        v_now = float(np.linalg.norm(traffic_agent.vehicle.velocity))

        # If no leader or no usable gap, fall back to zero accel (TrafficAgent will likely switch strategy next tick)
        if lead is None or gap_mm is None:
            traffic_agent.vehicle.setAcceleration(np.array([0.0, 0.0]))
            return

        # -------- parameters (mm, ms, mm/ms, mm/ms^2) ----------
        tau = float(getattr(traffic_agent, "reaction_time_ms", traffic_agent.time_headway * 1000.0))  # ms
        b_comf = float(traffic_agent.braking_comfortable)  # comfortable decel (mm/ms^2)
        b_hard = float(traffic_agent.b_max)                # hard decel cap (mm/ms^2)
        s0 = float(traffic_agent.smallest_follow_distance) # jam/standstill gap (mm)
        v_lead = float(np.linalg.norm(lead.vehicle.velocity))
        
        D_safe = float(getattr(traffic_agent, "emergency_distance", s0))

        # -------- safe speed (Gipps-style), aligned with report's "maximum safe speed" framing ----------
        # v_safe = -b * tau + sqrt( (b*tau)^2 + v_lead^2 + 2*b*(gap - s0) )
        # Clamp under the radical to avoid small numerical negatives.
        inside = (b_comf * tau) ** 2 + (v_lead ** 2) + 2.0 * b_comf * max(0.0, gap_mm - s0)
        v_safe = max(0.0, -b_comf * tau + np.sqrt(max(0.0, inside)))

        # Never accelerate in "brake" mode; aim no higher than current speed
        v_target = min(v_now, v_safe)

        # Safety deceleration needed to move toward v_target over the next step
        # (You can think of this as the "safety acceleration term" driven by safe speed.)
        a_safety = (v_target - v_now) / max(dt, 1.0)  # mm/ms^2 → will be ≤ 0

        if(gap_mm < D_safe):
            a_safety = self.big_brake(traffic_agent, v_lead, v_now, lead, b_hard, a_safety)
        # Anticipation of leader’s braking (the report’s “deceleration prediction term”):
        # If leader is much slower, bias toward stronger braking by blending in relative speed.
        dv = v_now - v_lead
        if dv > 0.0:
            # Extra braking proportional to closing speed; small gain keeps comfort.
            a_safety += - min(dv / max(tau, 1.0), b_comf)

        # Clip between comfortable and hard braking; do not allow positive accel in BrakeStrategy
        a_cmd = float(np.clip(a_safety, -b_hard, 0.0))

        # No backward roll when stopped
        if v_now < EPS and a_cmd < 0.0:
            a_cmd = 0.0

        # Apply along lane direction as a deceleration vector
        direction = traffic_agent.vehicle.velocity  # unit vector along lane
        # change_magnitude makes a +magnitude vector; negate to ensure we decelerate
        new_accel = -change_magnitude(direction, abs(a_cmd))
        traffic_agent.vehicle.setAcceleration(new_accel)
