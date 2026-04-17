import stisim as sti
import starsim as ss
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

##baseline (single - ng)
sim_ng = sti.Sim(diseases='ng', n_agents=2000, start=2010, stop=2030)
sim_ng.init()

ng = sim_ng.diseases.ng

sim_ng.run(verbose=0)
fig1 = sim_ng.plot(key=['ng.new_infections', 'ng.prevalence'])
fig1.suptitle('Gonorrhea Baseline — New Infections & Prevalence', fontsize=13, y=1.01)
plt.show()


##multi-sti comparison (ng, ct, tv)
sim_multi_default = sti.Sim(    #default parameters
    diseases=['ng', 'ct', 'tv'],
    n_agents=2000,
    start=2010,
    stop=2030,
)
sim_multi_default.run(verbose=0)
fig2 = sim_multi_default.plot(key=['ng.prevalence', 'ct.prevalence', 'tv.prevalence'])
fig2.suptitle('Multi-STI Comparison — Default Parameters', fontsize=13, y=1.01)
plt.show()

#custom paramters
sim_multi_custom = sti.Sim(
    diseases=['ng', 'ct', 'tv'],
    sti_pars=dict(
        ng=dict(beta_m2f=0.08, init_prev=0.03),   # NG: beta from Holmes et al.; prev from CDC 2022
        ct=dict(beta_m2f=0.08, init_prev=0.05),   # CT: beta similar to NG; prev from CDC 2022
        tv=dict(beta_m2f=0.12, init_prev=0.08),   # TV: higher beta; prev from WHO 2020
    ),
    n_agents=2000,
    start=2010,
    stop=2030,
)
sim_multi_custom.run(verbose=0)
fig3 = sim_multi_custom.plot(key=['ng.prevalence', 'ct.prevalence', 'tv.prevalence'])
fig3.suptitle('Multi-STI Comparison — Custom Parameters', fontsize=13, y=1.01)
plt.show()

#side-by-side comparison
fig4, axes = plt.subplots(1, 3, figsize=(15, 5))
diseases = [('ng', 'Gonorrhea'), ('ct', 'Chlamydia'), ('tv', 'Trichomoniasis')]
 
for ax, (key, name) in zip(axes, diseases):
    ax.plot(sim_multi_default.timevec,
            getattr(sim_multi_default.results, key).prevalence,
            label='Default', linestyle='--', color='steelblue')
    ax.plot(sim_multi_custom.timevec,
            getattr(sim_multi_custom.results, key).prevalence,
            label='Custom', color='firebrick')
    ax.set_title(name)
    ax.set_xlabel('Year')
    ax.set_ylabel('Prevalence')
    ax.legend()
    ax.grid(alpha=0.3)
 
fig4.suptitle('Default vs Custom Parameters — STI Prevalence Comparison', fontsize=13)
plt.tight_layout()
plt.show()


##beta sensitivity sweep - ng
beta_values = np.linspace(0.03, 0.20, 5)
sims_sweep = []
 
for b in beta_values:
    sim = sti.Sim(
        diseases=['ng'],
        sti_pars=dict(ng=dict(beta_m2f=b, init_prev=0.03)),
        n_agents=2000,
        start=2010,
        stop=2030,
        label=f'beta_m2f={b:.3f}'
    )
    sim.run(verbose=0)
    sims_sweep.append(sim)

fig5, axes = plt.subplots(1, 2, figsize=(14, 5))
colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(beta_values)))

for sim, color in zip(sims_sweep, colors):
    b_val = sim.label
    axes[0].plot(sim.timevec, sim.results.ng.prevalence,
                 label=b_val, color=color, lw=2)
    axes[1].plot(sim.timevec, sim.results.ng.new_infections,
                 label=b_val, color=color, lw=2)
 
for ax, title, ylabel in zip(axes,
    ['NG Prevalence by Beta', 'NG New Infections by Beta'],
    ['Prevalence', 'New Infections']):
    ax.set_xlabel('Year')
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.legend(fontsize=8)
    ax.grid(alpha=0.3)
 
fig5.suptitle('Gonorrhea Sensitivity Analysis — beta_m2f Sweep', fontsize=13)
plt.tight_layout()
plt.show()


##hiv + sti coinfection w/connectors
def make_hiv_sti_diseases():
    hiv  = sti.HIV(init_prev=0.10)
    ng   = sti.Gonorrhea(init_prev=0.03)
    ct   = sti.Chlamydia(init_prev=0.05)
    tv   = sti.Trichomoniasis(init_prev=0.08)
    return hiv, ng, ct, tv
 
# Without connectors
hiv, ng, ct, tv = make_hiv_sti_diseases()
sim_no_conn = sti.Sim(
    diseases=[hiv, ng, ct, tv],
    n_agents=2000, start=2010, stop=2030,
)
sim_no_conn.run(verbose=0)

# With connectors — STIs increase HIV susceptibility
# Source: CDC/WHO — NG increases HIV susceptibility ~1.2x, TV ~1.5x
hiv, ng, ct, tv = make_hiv_sti_diseases()
connectors = [
    sti.hiv_ng(hiv, ng),   # NG → HIV susceptibility 1.2x
    sti.hiv_ct(hiv, ct),   # CT → HIV susceptibility 1.0x
    sti.hiv_tv(hiv, tv),   # TV → HIV susceptibility 1.5x
]
sim_with_conn = sti.Sim(
    diseases=[hiv, ng, ct, tv],
    connectors=connectors,
    n_agents=2000, start=2010, stop=2030,
)
sim_with_conn.run(verbose=0)

# Compare HIV outcomes with and without STI connectors
fig6, axes = plt.subplots(1, 3, figsize=(15, 5))
 
axes[0].plot(sim_no_conn.timevec,   sim_no_conn.results.hiv.prevalence,   label='No connectors', linestyle='--')
axes[0].plot(sim_with_conn.timevec, sim_with_conn.results.hiv.prevalence, label='With STI connectors')
axes[0].set_title('HIV Prevalence'); axes[0].set_xlabel('Year')
axes[0].set_ylabel('Prevalence'); axes[0].legend(); axes[0].grid(alpha=0.3)
 
axes[1].plot(sim_no_conn.timevec,   sim_no_conn.results.hiv.new_infections,   label='No connectors', linestyle='--')
axes[1].plot(sim_with_conn.timevec, sim_with_conn.results.hiv.new_infections, label='With STI connectors')
axes[1].set_title('HIV New Infections'); axes[1].set_xlabel('Year')
axes[1].set_ylabel('New Infections'); axes[1].legend(); axes[1].grid(alpha=0.3)
 
axes[2].plot(sim_no_conn.timevec,   sim_no_conn.results.ng.prevalence,   label='NG (no conn)', linestyle='--', color='steelblue')
axes[2].plot(sim_with_conn.timevec, sim_with_conn.results.ng.prevalence, label='NG (with conn)', color='steelblue')
axes[2].plot(sim_no_conn.timevec,   sim_no_conn.results.ct.prevalence,   label='CT (no conn)', linestyle='--', color='firebrick')
axes[2].plot(sim_with_conn.timevec, sim_with_conn.results.ct.prevalence, label='CT (with conn)', color='firebrick')
axes[2].set_title('STI Prevalence'); axes[2].set_xlabel('Year')
axes[2].set_ylabel('Prevalence'); axes[2].legend(fontsize=7); axes[2].grid(alpha=0.3)
 
fig6.suptitle('HIV + STI Coinfection: Effect of Biological Connectors', fontsize=13)
plt.tight_layout()
plt.show()

#quantifying connector effect
final_hiv_no_conn   = sim_no_conn.results.hiv.cum_infections[-1]
final_hiv_with_conn = sim_with_conn.results.hiv.cum_infections[-1]
pct_increase = (final_hiv_with_conn - final_hiv_no_conn) / final_hiv_no_conn * 100
print(f"\n── Connector Effect ─────────────────────────────────────")
print(f"  Cumulative HIV (no connectors):   {final_hiv_no_conn:.0f}")
print(f"  Cumulative HIV (with connectors): {final_hiv_with_conn:.0f}")
print(f"  Increase due to STI connectors:   {pct_increase:.1f}%")