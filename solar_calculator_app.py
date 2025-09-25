# solar_calculator_app.py
import streamlit as st
import pandas as pd
import numpy as np

# Custom CSS to match your design
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        color: #2e86ab;
        border-bottom: 2px solid #2e86ab;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
    .load-table {
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    .load-table th, .load-table td {
        padding: 12px;
        text-align: left;
        border-bottom: 1px solid #ddd;
    }
    .load-table th {
        background-color: #f2f2f2;
        font-weight: bold;
    }
    .button-small {
        padding: 4px 8px;
        margin: 0 2px;
        font-size: 12px;
    }
    .add-load-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

class SolarDemandCalculator:
    COMMERCIAL_APPLIANCES = {
        'LED Light': {'power_w': 20, 'typical_hours': 8},
        'Refrigerator': {'power_w': 300, 'typical_hours': 24},
        'Computer': {'power_w': 150, 'typical_hours': 8},
        'AC Unit': {'power_w': 1500, 'typical_hours': 6},
        'Water Pump': {'power_w': 750, 'typical_hours': 4},
        'Ventilation Fan': {'power_w': 100, 'typical_hours': 12},
        'Printer': {'power_w': 100, 'typical_hours': 2},
        'Security Camera': {'power_w': 50, 'typical_hours': 24}
    }
    
    def __init__(self, system_voltage=48):
        self.system_voltage = system_voltage
        self.loads = []
    
    def add_load(self, description, power_w, quantity, hours_per_day):
        self.loads.append({
            'description': description,
            'power_w': power_w,
            'quantity': quantity,
            'hours_per_day': hours_per_day,
            'daily_energy_wh': power_w * quantity * hours_per_day
        })
    
    def calculate_demand(self):
        if not self.loads:
            return {
                'total_energy_wh': 0,
                'total_energy_kwh': 0,
                'total_ah': 0,
                'peak_power_w': 0
            }
        
        total_energy_wh = sum(load['daily_energy_wh'] for load in self.loads)
        peak_power_w = sum(load['power_w'] * load['quantity'] for load in self.loads)
        
        return {
            'total_energy_wh': total_energy_wh,
            'total_energy_kwh': total_energy_wh / 1000,
            'total_ah': total_energy_wh / self.system_voltage,
            'peak_power_w': peak_power_w
        }

def main():
    st.set_page_config(
        page_title="Commercial Solar PV System Designer",
        page_icon="☀️",
        layout="wide"
    )
    
    # Header
    st.markdown('<h1 class="main-header">Commercial Solar PV System Designer</h1>', unsafe_allow_html=True)
    st.markdown('### Simple Load Calculator')
    
    # Initialize session state
    if 'calculator' not in st.session_state:
        st.session_state.calculator = SolarDemandCalculator()
    if 'loads' not in st.session_state:
        st.session_state.loads = []
    
    # Add Electrical Load Section
    st.markdown('<div class="section-header">Add Electrical Load</div>', unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="add-load-section">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
        
        with col1:
            appliance_name = st.selectbox(
                "Appliance Name",
                options=list(st.session_state.calculator.COMMERCIAL_APPLIANCES.keys()),
                key="appliance_select"
            )
            # Allow custom appliance name
            custom_name = st.text_input("Or enter custom appliance:", key="custom_name")
        
        with col2:
            if custom_name:
                power_w = st.number_input("Power (W)", min_value=1, value=100, key="custom_power")
            else:
                default_power = st.session_state.calculator.COMMERCIAL_APPLIANCES[appliance_name]['power_w']
                power_w = st.number_input("Power (W)", min_value=1, value=default_power, key="power_input")
        
        with col3:
            quantity = st.number_input("Quantity", min_value=1, value=1, key="quantity_input")
        
        with col4:
            if custom_name:
                hours_per_day = st.number_input("Hours per Day", min_value=1, max_value=24, value=8, key="custom_hours")
            else:
                default_hours = st.session_state.calculator.COMMERCIAL_APPLIANCES[appliance_name]['typical_hours']
                hours_per_day = st.number_input("Hours per Day", min_value=1, max_value=24, value=default_hours, key="hours_input")
        
        col1, col2 = st.columns([4, 1])
        with col2:
            if st.button("Add Load", type="primary", use_container_width=True):
                name_to_use = custom_name if custom_name else appliance_name
                st.session_state.calculator.add_load(name_to_use, power_w, quantity, hours_per_day)
                st.session_state.loads = st.session_state.calculator.loads
                st.success(f"✅ Added {name_to_use}")
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display Current Loads
    if st.session_state.loads:
        st.markdown("### Current Electrical Loads")
        
        # Create a DataFrame for better display
        load_data = []
        for i, load in enumerate(st.session_state.loads):
            load_data.append({
                'Appliance': load['description'],
                'Power (W)': load['power_w'],
                'Quantity': load['quantity'],
                'Hours/Day': load['hours_per_day'],
                'Daily Energy (Wh)': load['daily_energy_wh']
            })
        
        df = pd.DataFrame(load_data)
        
        # Display the table with custom styling
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
        
        # Add delete buttons for each load
        cols = st.columns(len(st.session_state.loads))
        for i, load in enumerate(st.session_state.loads):
            with cols[i]:
                if st.button(f"🗑️ Delete {load['description']}", key=f"del_{i}"):
                    st.session_state.calculator.loads.pop(i)
                    st.session_state.loads = st.session_state.calculator.loads
                    st.rerun()
        
        # Calculate and display results
        results = st.session_state.calculator.calculate_demand()
        
        st.markdown("---")
        st.markdown("### 📊 Energy Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Daily Energy", 
                f"{results['total_energy_kwh']:.2f} kWh",
                help="Total energy consumption per day"
            )
        
        with col2:
            st.metric(
                "Peak Power Demand", 
                f"{results['peak_power_w']/1000:.2f} kW",
                help="Maximum instantaneous power requirement"
            )
        
        with col3:
            st.metric(
                "Battery Capacity Needed", 
                f"{results['total_ah']:.0f} Ah",
                help="At 48V system voltage"
            )
        
        with col4:
            # Simple solar panel estimate (4.5 sun hours per day)
            pv_size = results['total_energy_kwh'] / 4.5
            st.metric(
                "PV System Size", 
                f"{pv_size:.2f} kW",
                help="Estimated solar panel capacity needed"
            )
        
        # Clear all button
        if st.button("Clear All Loads", type="secondary"):
            st.session_state.calculator.loads = []
            st.session_state.loads = []
            st.rerun()
        
        # Progress to next steps
        st.markdown("---")
        st.markdown("### Next Steps")
        
        tab1, tab2, tab3 = st.tabs(["📋 System Design", "💰 Cost Estimate", "🔧 Implementation"])
        
        with tab1:
            st.write("**Complete System Design**")
            st.write("Based on your load assessment, we recommend:")
            st.write(f"- **Solar Panels**: {pv_size:.1f} kW system")
            st.write(f"- **Battery Bank**: {results['total_energy_kwh'] * 2:.1f} kWh (2 days autonomy)")
            st.write(f"- **Inverter**: {results['peak_power_w']/1000 * 1.2:.1f} kW with 20% safety margin")
        
        with tab2:
            st.write("**Cost Estimation**")
            equipment_cost = pv_size * 1200 + (results['total_energy_kwh'] * 2) * 600
            total_cost = equipment_cost * 1.3  # Including installation
            st.write(f"- Equipment: ${equipment_cost:,.0f}")
            st.write(f"- Installation: ${equipment_cost * 0.3:,.0f}")
            st.write(f"- **Total Estimated Cost: ${total_cost:,.0f}**")
        
        with tab3:
            st.write("**Implementation Timeline**")
            st.write("1. Site assessment (1 week)")
            st.write("2. System design finalization (1 week)")
            st.write("3. Equipment procurement (2-4 weeks)")
            st.write("4. Installation (1-2 weeks)")
            st.write("5. Commissioning and testing (1 week)")
    
    else:
        # Empty state message
        st.markdown("---")
        st.info("### 💡 Add some electrical loads to get started!")
        st.write("Use the form above to add your appliances and see your solar system requirements.")
        
        # Quick start examples
        st.markdown("#### 💡 Quick Start Examples:")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🏢 Small Office Setup"):
                st.session_state.calculator.add_load("LED Lights", 20, 15, 10)
                st.session_state.calculator.add_load("Computers", 150, 5, 8)
                st.session_state.calculator.add_load("AC Unit", 1500, 1, 6)
                st.session_state.loads = st.session_state.calculator.loads
                st.rerun()
        
        with col2:
            if st.button("🏪 Retail Store Setup"):
                st.session_state.calculator.add_load("LED Lights", 20, 30, 12)
                st.session_state.calculator.add_load("Refrigerator", 300, 2, 24)
                st.session_state.calculator.add_load("AC Unit", 1500, 2, 8)
                st.session_state.loads = st.session_state.calculator.loads
                st.rerun()
        
        with col3:
            if st.button("🏭 Workshop Setup"):
                st.session_state.calculator.add_load("LED Lights", 20, 20, 10)
                st.session_state.calculator.add_load("Power Tools", 1000, 3, 4)
                st.session_state.calculator.add_load("Ventilation", 200, 2, 8)
                st.session_state.loads = st.session_state.calculator.loads
                st.rerun()

if __name__ == "__main__":
    main()