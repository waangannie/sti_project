import stisim as sti
import hivsim
import starsim as ss
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

##baseline vs testing + ART
# Baseline: no interventions
sim_base = hivsim.demo('simple', run=False, plot=False, n_agents=3000)
sim_base.pars.interventions = []
sim_base.run(verbose=0)
 
# Custom testing + time-varying ART coverage
# Source: UNAIDS 90-90-90 targets; national ART program data
hiv_test = sti.HIVTest(
    test_prob_data=0.2,    # 20% annual testing probability | Source: DHS survey data
    start=2000,
    name='hiv_test'
)
art = sti.ART(
    coverage={'year': [2000, 2010, 2025], 'value': [0, 0.5, 0.9]}
    # Coverage ramp-up | Source: UNAIDS ART coverage data
    # 0% in 2000 (pre-rollout), 50% by 2010, 90% by 2025 (UNAIDS target)
)
 
sim_intv = hivsim.demo('simple', run=False, plot=False, n_agents=3000)
sim_intv.pars.interventions = [hiv_test, art]
sim_intv.run(verbose=0)

# Plot comparison
fig1, axes = plt.subplots(1, 3, figsize=(15, 5))
 
axes[0].plot(sim_base.timevec,  sim_base.results.hiv.prevalence_15_49,  label='No interventions', linestyle='--', color='firebrick')
axes[0].plot(sim_intv.timevec, sim_intv.results.hiv.prevalence_15_49, label='Testing + ART', color='steelblue')
axes[0].set_xlabel('Year'); axes[0].set_ylabel('HIV prevalence (15–49)')
axes[0].set_title('HIV Prevalence'); axes[0].legend(); axes[0].grid(alpha=0.3)
 
axes[1].plot(sim_base.timevec,  sim_base.results.hiv.new_infections,  label='No interventions', linestyle='--', color='firebrick')
axes[1].plot(sim_intv.timevec, sim_intv.results.hiv.new_infections, label='Testing + ART', color='steelblue')
axes[1].set_xlabel('Year'); axes[1].set_ylabel('New HIV infections')
axes[1].set_title('New Infections'); axes[1].legend(); axes[1].grid(alpha=0.3)
 
axes[2].plot(sim_intv.timevec, sim_intv.results.hiv.n_on_art, color='green')
axes[2].set_xlabel('Year'); axes[2].set_ylabel('Number on ART')
axes[2].set_title('ART Uptake'); axes[2].grid(alpha=0.3)
 
fig1.suptitle('HIV: Baseline vs Testing + ART Intervention', fontsize=13)
plt.tight_layout()
plt.show()

# quantifying impact
final_prev_base  = sim_base.results.hiv.prevalence_15_49[-1]
final_prev_intv  = sim_intv.results.hiv.prevalence_15_49[-1]
total_inf_base   = sim_base.results.hiv.cum_infections[-1]
total_inf_intv   = sim_intv.results.hiv.cum_infections[-1]
inf_averted      = total_inf_base - total_inf_intv
pct_reduction    = inf_averted / total_inf_base * 100

print(f"\n── Section 1 Results ────────────────────────────────────")
print(f"  Final prevalence (no intervention): {final_prev_base:.3f}")
print(f"  Final prevalence (testing + ART):   {final_prev_intv:.3f}")
print(f"  Infections averted:                 {inf_averted:.0f}")
print(f"  % reduction:                        {pct_reduction:.1f}%")
    #7.7% reduduction in testing + ART


##targeted interventions vs general population
# Scenario A: Uniform testing (no targeting)
test_uniform = sti.HIVTest(
    test_prob_data=0.1,
    start=2000,
    name='uniform_test'
)
 
# Scenario B: Targeted — higher rate for FSW, lower for general population
# Source: WHO consolidated guidelines on HIV; FSW testing recommendations
fsw_test = sti.HIVTest(
    test_prob_data=0.3,                       # 30% for FSW | Source: WHO FSW guidelines
    start=2000,
    name='fsw_test',
    eligibility=lambda sim: sim.networks.structuredsexual.fsw & ~sim.diseases.hiv.diagnosed,
)
gp_test = sti.HIVTest(
    test_prob_data=0.05,                      # 5% general pop | Source: DHS survey data
    start=2000,
    name='gp_test',
    eligibility=lambda sim: ~sim.networks.structuredsexual.fsw & ~sim.diseases.hiv.diagnosed,
)
 
art_shared = sti.ART(coverage=0.8)

# Run both scenarios
sim_uniform = hivsim.demo('simple', run=False, plot=False, n_agents=3000)
sim_uniform.pars.interventions = [test_uniform, sti.ART(coverage=0.8)]
sim_uniform.run(verbose=0)
 
sim_targeted = hivsim.demo('simple', run=False, plot=False, n_agents=3000)
sim_targeted.pars.interventions = [fsw_test, gp_test, art_shared]
sim_targeted.run(verbose=0)
 
fig3, axes = plt.subplots(1, 2, figsize=(14, 5))
 
axes[0].plot(sim_uniform.timevec,  sim_uniform.results.hiv.prevalence_15_49,  label='Uniform testing (10%)', linestyle='--', color='steelblue')
axes[0].plot(sim_targeted.timevec, sim_targeted.results.hiv.prevalence_15_49, label='Targeted (FSW 30%, GP 5%)', color='firebrick')
axes[0].set_xlabel('Year'); axes[0].set_ylabel('HIV Prevalence (15–49)')
axes[0].set_title('Prevalence: Uniform vs Targeted Testing')
axes[0].legend(); axes[0].grid(alpha=0.3)
 
axes[1].plot(sim_uniform.timevec,  sim_uniform.results.hiv.new_infections,  label='Uniform testing', linestyle='--', color='steelblue')
axes[1].plot(sim_targeted.timevec, sim_targeted.results.hiv.new_infections, label='Targeted testing', color='firebrick')
axes[1].set_xlabel('Year'); axes[1].set_ylabel('New HIV Infections')
axes[1].set_title('New Infections: Uniform vs Targeted')
axes[1].legend(); axes[1].grid(alpha=0.3)
 
fig3.suptitle('Targeted vs Uniform HIV Testing Strategies', fontsize=13)
plt.tight_layout()
plt.show()

#quantifying targeting benefit
inf_uniform  = sim_uniform.results.hiv.cum_infections[-1]
inf_targeted = sim_targeted.results.hiv.cum_infections[-1]
targeting_benefit = (inf_uniform - inf_targeted) / inf_uniform * 100
print(f"\n── Targeting Benefit ────────────────────────────────────")
print(f"  Cumulative infections (uniform):   {inf_uniform:.0f}")
print(f"  Cumulative infections (targeted):  {inf_targeted:.0f}")
print(f"  Additional reduction from targeting: {targeting_benefit:.1f}%")
    #5.8% reduction from targeting