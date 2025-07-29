
#region WF_chiller_data

WF_chiller_fault_list=["chiller_liquid_line_probe_fail",
                    "chiller_aft_probe_fail",
                    "chiller_room_temp_probe_ht_fault",
                    "chiller_room_temp_probe_lt_fault",
                    "chiller_pump_overload_fault",
                    "chiller_compressor_overload_fault",
                    "chiller_hp_fault",
                    "chiller_lp_fault",                    
                    "chiller_low_liquid_level_fault",                    
                    "chiller_high_temp_fault",
                    "chiller_aft_fault"]


WF_chiller_data={    
    "chiller_liquid_temp":10,
    "chiller_aft_temp":20,

    "chiller_room_temp_probe_fail":0,
    "chiller_aft_probe_fail":0,
    "chiller_room_temp_probe_ht_fault":0,
    "chiller_room_temp_probe_lt_fault":0,
    
    "chiller_pump_overload_fault":0,
    "chiller_spp_fault":0,
    "chiller_compressor_overload_fault":0,
    "chiller_hp_fault":0,
    "chiller_lp_fault":0,

    "chiller_low_liquid_level_fault":0,
    "chiller_liquid_line_high_temp_fault":0,    
    "chiller_high_temp_fault":0,
    "chiller_aft_fault":0,
    
    "chiller_compressor_on":0,
    "chiller_pump_on":0,
    "chiller_sv_on":0,
    "chiller_alarm_on":0,

    "chiller_set_high_set":40,
    "chiller_set_low_set":9,
    "chiller_set_set_point":10,
    "chiller_set_differential":2,
    "chiller_set_high_temp_alarm":50,
    "chiller_set_low_temp_alarm":8,
    "chiller_set_aft_set_temp":4,
    "chiller_set_aft_differential":2,
    "chiller_remote_start":1,

    }

WF_chiller_data_base={
    
    "chiller_liquid_temp":10,
    "chiller_aft_temp":20,

    "chiller_room_temp_probe_fail":0,
    "chiller_aft_probe_fail":0,
    "chiller_room_temp_probe_ht_fault":0,
    "chiller_room_temp_probe_lt_fault":0,
    
    "chiller_pump_overload_fault":0,
    "chiller_spp_fault":0,
    "chiller_compressor_overload_fault":0,
    "chiller_hp_fault":0,
    "chiller_lp_fault":0,

    "chiller_low_liquid_level_fault":0,
    "chiller_liquid_line_high_temp_fault":0,
    "chiller_high_temp_fault":0,
    "chiller_aft_fault":0,
    
    "chiller_compressor_on":0,
    "chiller_pump_on":0,
    "chiller_sv_on":0,
    "chiller_alarm_on":0,

    "chiller_set_high_set":40,
    "chiller_set_low_set":9,
    "chiller_set_set_point":10,
    "chiller_set_differential":2,
    "chiller_set_high_temp_alarm":50,
    "chiller_set_low_temp_alarm":8,
    "chiller_set_aft_set_temp":4,
    "chiller_set_aft_differential":2,
    "chiller_remote_start":1,

    }

#endregion WF_chiller_data

#region WF_heater_data

WF_heater_data={
    'heater_tank_temperature':25,

    'heater_relay_sts_compressor':1,
    'heater_relay_sts_alarm':1,

    'heater_fault_sts_probe_fail_low':0,
    'heater_fault_sts_probe_fail_high':0,
    'heater_fault_sts_ht':0,
    'heater_fault_sts_lt':0,
    'heater_fault_water_level_low':0,
    'heater_fault':0,

    'heater_run_hours':20,
    "heater_set_point":50,
    
    "heater_high_temp_limit":55,
    "heater_high_temp_alarm_diff":2,
    "heater_low_temp_limit":40,
    "heater_low_temp_alarm_diff":2,
    
    "heater_max_set_point_limit":52,
    "heater_min_set_point_limit":42,
    "heater_relay_on_differential":5,
    "heater_probe_calibration":0,    
    "heater_relay_min_on_time":0,
    "heater_fault_condition_when_probe_fail":0
    }


WF_heater_base_data={
    'heater_tank_temperature':25,

    'heater_relay_sts_compressor':1,
    'heater_relay_sts_alarm':1,

    'heater_fault_sts_probe_fail_low':0,
    'heater_fault_sts_probe_fail_high':0,
    'heater_fault_sts_ht':0,
    'heater_fault_sts_lt':0,
    'heater_fault_water_level_low':0,
    'heater_fault':0,

    'heater_run_hours':20,
    "heater_set_point":50,
    "heater_high_temp_limit":55,
    "heater_high_temp_alarm_diff":2,
    "heater_low_temp_limit":40,
    "heater_low_temp_alarm_diff":2,
    
    "heater_max_set_point_limit":52,
    "heater_min_set_point_limit":42,
    "heater_relay_on_differential":5,
    "heater_probe_calibration":0,    
    "heater_relay_min_on_time":0,
    "heater_fault_condition_when_probe_fail":0
    }

WF_heater_registers={    
    'heater_tank_temperature':6,
    'relay_status':11,
    'fault_status':12,

    'heater_run_hours':14,
    "heater_set_point":31,
    "heater_high_temp_limit":33,
    "heater_high_temp_alarm_diff":34,
    "heater_low_temp_limit":35,
    "heater_low_temp_alarm_diff":36,
    
    "heater_max_set_point_limit":37,
    "heater_min_set_point_limit":38,
    "heater_relay_on_differential":39,
    "heater_probe_calibration":40,    
    "heater_relay_min_on_time":42,
    "heater_fault_condition_when_probe_fail":43    
    }



#endregion WF_heater_data

#region LT_AC_EM_data

### byte 1 controls the data after decimal
### byte 2 controls that data before decimal point

LT_AC_EM_data_dict={
        'em_watts_total':0,
        'em_watts_r_phase':0,
        'em_watts_y_phase':0,
        'em_watts_b_phase':0,

        'em_power_factor_avg':0.8,
        'em_power_factor_r_phase':0.7,
        'em_power_factor_y_phase':0.5,
        'em_power_factor_b_phase':0.9,

        'em_apparent_power_total':0,
        'em_apparent_power_r_phase':0,
        'em_apparent_power_y_phase':0,
        'em_apparent_power_b_phase':0,

        'em_voltage_ll_avg':440,
        'em_voltage_ry_phase':440,
        'em_voltage_yb_phase':440,
        'em_voltage_br_phase':440,

        'em_voltage_ln_avg':220.6,
        'em_voltage_r_phase':250.5,
        'em_voltage_y_phase':210.4,
        'em_voltage_b_phase':234.8,

        'em_current_total':0,
        'em_current_r_phase':0,
        'em_current_y_phase':0,
        'em_current_b_phase':0,

        'em_frequency':0,
        'em_k_watt_hour':0,
        'em_voltage_ampere_hour':0,

}


LT_AC_EM_data_dict_base={
        'em_watts_total':0,
        'em_watts_r_phase':0,
        'em_watts_y_phase':0,
        'em_watts_b_phase':0,

        'em_power_factor_avg':0.8,
        'em_power_factor_r_phase':0.7,
        'em_power_factor_y_phase':0.5,
        'em_power_factor_b_phase':0.9,

        'em_apparent_power_total':0,
        'em_apparent_power_r_phase':0,
        'em_apparent_power_y_phase':0,
        'em_apparent_power_b_phase':0,

        'em_voltage_ll_avg':440,
        'em_voltage_ry_phase':440,
        'em_voltage_yb_phase':440,
        'em_voltage_br_phase':440,

        'em_voltage_ln_avg':220.6,
        'em_voltage_r_phase':250.5,
        'em_voltage_y_phase':210.4,
        'em_voltage_b_phase':234.8,

        'em_current_total':0,
        'em_current_r_phase':0,
        'em_current_y_phase':0,
        'em_current_b_phase':0,

        'em_frequency':0,
        'em_k_watt_hour':0,
        'em_voltage_ampere_hour':0,

}

LT_AC_EM_registers_dict={
            'em_watts_total_b1':101,
            'em_watts_r_phase_b1':103,
            'em_watts_y_phase_b1':105,
            'em_watts_b_phase_b1':107,

            'em_power_factor_avg_b1':117,
            'em_power_factor_r_phase_b1':119,
            'em_power_factor_y_phase_b1':121,
            'em_power_factor_b_phase_b1':123,

            'em_apparent_power_total_b1':125,
            'em_apparent_power_r_phase_b1':127,
            'em_apparent_power_y_phase_b1':129,
            'em_apparent_power_b_phase_b1':131,

            'em_voltage_ll_avg_b1':133,
            'em_voltage_ry_phase_b1':135,
            'em_voltage_yb_phase_b1':137,
            'em_voltage_br_phase_b1':139,

            'em_voltage_ln_avg_b1':141,
            'em_voltage_r_phase_b1':143,
            'em_voltage_y_phase_b1':145,
            'em_voltage_b_phase_b1':147,

            'em_current_total_b1':149,
            'em_current_r_phase_b1':151,
            'em_current_y_phase_b1':153,
            'em_current_b_phase_b1':155,

            'em_frequency_b1':157,
            'em_k_watt_hour_b1':159,
            'em_voltage_ampere_hour_b1':161,

            'em_watts_total_b2':102,
            'em_watts_r_phase_b2':104,
            'em_watts_y_phase_b2':106,
            'em_watts_b_phase_b2':108,

            'em_power_factor_avg_b2':118,
            'em_power_factor_r_phase_b2':120,
            'em_power_factor_y_phase_b2':122,
            'em_power_factor_b_phase_b2':124,

            'em_apparent_power_total_b2':126,
            'em_apparent_power_r_phase_b2':128,
            'em_apparent_power_y_phase_b2':130,
            'em_apparent_power_b_phase_b2':132,

            'em_voltage_ll_avg_b2':134,
            'em_voltage_ry_phase_b2':136,
            'em_voltage_yb_phase_b2':138,
            'em_voltage_br_phase_b2':140,

            'em_voltage_ln_avg_b2':142,
            'em_voltage_r_phase_b2':144,
            'em_voltage_y_phase_b2':146,
            'em_voltage_b_phase_b2':148,

            'em_current_total_b2':150,
            'em_current_r_phase_b2':152,
            'em_current_y_phase_b2':154,
            'em_current_b_phase_b2':156,

            'em_frequency_b2':158,
            'em_k_watt_hour_b2':160,
            'em_voltage_ampere_hour_b2':162        
        }

#endregion LT_AC_EM_data