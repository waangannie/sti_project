import stisim as sti

sim = sti.Sim(diseases='ng') #ng is gonorrhea
sim.run(verbose=0)
sim.plot(key=['ng.new_infections', 'ng.prevalence'])

#simulation parameters
sim = sti.Sim(diseases='ng')
sim.init()

print(f'Start:    {sim.pars.start}')
print(f'Stop:     {sim.pars.stop}')
print(f'Timestep: {sim.pars.dt} years ({sim.pars.dt*12:.0f} month)')
print(f'Agents:   {sim.pars.n_agents}')

#networks
for name, nw in sim.networks.items():
    print(f'{name}: {type(nw).__name__}')

#disease
ng = sim.diseases.ng
print(f'Disease: {type(ng).__name__}')
print(f'Transmission (M to F): {ng.pars.beta_m2f}')
print(f'Initial prevalence: {ng.pars.init_prev}')
print(f'Condom efficacy: {ng.pars.eff_condom}')

#demographics
print(f'Demographics: {dict(sim.demographics)}')
print(f'(Empty by default -- pass demographics="zimbabwe" to auto-load demographic data)')



##customizing the simulation

#Passing parameters inline
sim = sti.Sim(
    diseases='ng',
    n_agents=2000,
    start=2010,
    stop=2025,
)
sim.run(verbose=0)

#Passing disease-specific parameters
sim = sti.Sim(
    diseases=['ng', 'ct'],
    sti_pars=dict(              #Use sti_pars to override disease defaults without creating the disease object yourself
        ng=dict(init_prev=0.05),
        ct=dict(init_prev=0.08), #ct = chlamydia
    ),
)
sim.run(verbose=0)



##using module instances

#the standard Starsim pattern and gives you access to every parameter
import starsim as ss

ng = sti.Gonorrhea(beta_m2f=0.08, init_prev=0.03)
nw = sti.StructuredSexual()
pregnancy = ss.Pregnancy(fertility_rate=20)
deaths = ss.Deaths(death_rate=10)

sim = sti.Sim(
    diseases=ng,
    networks=nw,
    demographics=[pregnancy, deaths],
    n_agents=2000,
    start=2010,
    stop=2030,
)
sim.run(verbose=0)
sim.plot(key=['ng.new_infections', 'ng.prevalence'])


##Multiple STIs on a shared network + Customizing disease parameters
sim = sti.Sim(
    diseases=['ng', 'ct', 'tv'],
    n_agents=2000,
    start=2010,
    stop=2030,
)
sim.run(verbose=0)
sim.plot(key=['ng.prevalence', 'ct.prevalence', 'tv.prevalence'])

sim = sti.Sim(
    diseases=['ng', 'ct', 'tv'],
    sti_pars=dict(
        ng=dict(beta_m2f=0.08, init_prev=0.03),
        ct=dict(beta_m2f=0.08, init_prev=0.05),
        tv=dict(beta_m2f=0.12, init_prev=0.08),
    ),
    n_agents=2000,
    start=2010,
    stop=2030,
)
sim.run(verbose=0)
sim.plot(key=['ng.prevalence', 'ct.prevalence', 'tv.prevalence'])


##Adding HIV with connectors
# Create disease modules
hiv = sti.HIV(init_prev=0.10)
ng = sti.Gonorrhea(init_prev=0.03)
ct = sti.Chlamydia(init_prev=0.05)
tv = sti.Trichomoniasis(init_prev=0.08)

# Create connectors for HIV-STI interactions
connectors = [
    sti.hiv_ng(hiv, ng),   # NG increases HIV susceptibility (default: 1.2x)
    sti.hiv_ct(hiv, ct),   # CT increases HIV susceptibility (default: 1.0x)
    sti.hiv_tv(hiv, tv),   # TV increases HIV susceptibility (default: 1.5x)
]

sim = sti.Sim(
    diseases=[hiv, ng, ct, tv],
    connectors=connectors,
    n_agents=2000,
    start=2010,
    stop=2030,
)
sim.run(verbose=0)
sim.plot(key=['hiv.prevalence', 'ng.prevalence', 'ct.prevalence', 'tv.prevalence'])



##comparing w/ and w/o connectors
import matplotlib.pyplot as plt
import starsim as ss

def make_diseases():
    """ Helper to create fresh disease modules """
    hiv = sti.HIV(init_prev=0.02, beta_m2f=0.03)
    syph = sti.Syphilis(
        init_prev=0.10, beta_m2f=0.25,
        rel_trans_primary=5, rel_trans_latent=0.1,
        eff_condom=0.5,
        dur_primary=ss.constant(v=ss.years(2)),  # Extended for illustration
    )
    return hiv, syph

# Without connectors
hiv, syph = make_diseases()
s0 = sti.Sim(diseases=[hiv, syph], n_agents=5000, start=2000, stop=2020)
s0.run(verbose=0)

# With connectors -- syphilis increases HIV susceptibility 2.67x (default)
hiv, syph = make_diseases()
s1 = sti.Sim(
    diseases=[hiv, syph],
    connectors=sti.hiv_syph(hiv, syph),
    n_agents=5000, start=2000, stop=2020,
)
s1.run(verbose=0)

# Compare cumulative HIV infections
fig, ax = plt.subplots()
ax.plot(s0.timevec, s0.results.hiv.cum_infections, label='Without connector')
ax.plot(s1.timevec, s1.results.hiv.cum_infections, label='With hiv_syph connector')
ax.set_xlabel('Year')
ax.set_ylabel('Cumulative HIV infections')
ax.set_title('Effect of syphilis coinfection on HIV acquisition')
ax.legend()
fig
plt.show() #have to use this for plot to show here


##interventions

#simple treatment
import stisim as sti
import starsim as ss
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Baseline: no treatment
sim_base = sti.Sim(diseases='ng', n_agents=2000, start=2010, stop=2030)
sim_base.run(verbose=0)

# With treatment: symptomatic care-seekers get treated
ng = sti.Gonorrhea(init_prev=0.01)
ng_tx = sti.GonorrheaTreatment(
    name='ng_tx',
    eligibility=lambda sim: sim.diseases.ng.symptomatic & (sim.diseases.ng.ti_seeks_care == sim.ti),
)
sim_intv = sti.Sim(diseases=ng, interventions=[ng_tx], n_agents=2000, start=2010, stop=2030)
sim_intv.run(verbose=0)

fig, ax = plt.subplots()
ax.plot(sim_base.timevec, sim_base.results.ng.prevalence, label='No treatment')
ax.plot(sim_intv.timevec, sim_intv.results.ng.prevalence, label='Treatment for care-seekers')
ax.set_xlabel('Year')
ax.set_ylabel('NG prevalence')
ax.set_title('Effect of treatment on gonorrhea')
ax.legend()
fig
plt.show()


##HIV testing and ART
import hivsim

# Simplest approach: use hivsim.demo which includes testing + ART by default
sim_default = hivsim.demo('simple', run=False, plot=False, n_agents=3000)
sim_default.run(verbose=0)

# Custom: specify coverage explicitly
hiv_test = sti.HIVTest(test_prob_data=0.2, start=2000, name='hiv_test')

# ART with time-varying coverage (proportion of infected)
art = sti.ART(coverage={'year': [2000, 2010, 2025], 'value': [0, 0.5, 0.9]})

# Without any interventions for comparison
sim_base = hivsim.demo('simple', run=False, plot=False, n_agents=3000)
sim_base.pars.interventions = []
sim_base.run(verbose=0)

# With custom testing + ART
sim_intv = hivsim.demo('simple', run=False, plot=False, n_agents=3000)
sim_intv.pars.interventions = [hiv_test, art]
sim_intv.run(verbose=0)

fig, axes = plt.subplots(1, 3, figsize=(14, 4))

axes[0].plot(sim_base.timevec, sim_base.results.hiv.prevalence_15_49, label='No interventions', alpha=0.7)
axes[0].plot(sim_intv.timevec, sim_intv.results.hiv.prevalence_15_49, label='Testing + ART', alpha=0.7)
axes[0].set_xlabel('Year')
axes[0].set_ylabel('HIV prevalence (15-49)')
axes[0].legend()

axes[1].plot(sim_intv.timevec, sim_intv.results.hiv.new_infections, alpha=0.7)
axes[1].set_xlabel('Year')
axes[1].set_ylabel('New HIV infections')
axes[1].set_title('Infections with ART')

axes[2].plot(sim_intv.timevec, sim_intv.results.hiv.n_on_art)
axes[2].set_xlabel('Year')
axes[2].set_ylabel('Number on ART')
axes[2].set_title('ART uptake')

plt.tight_layout()
fig
plt.show()


##Targeting interventions - Use the eligibility parameter to target interventions to specific populations
# Higher testing rate for FSWs
fsw_test = sti.HIVTest(
    test_prob_data=0.3,
    start=2000,
    name='fsw_test',
    eligibility=lambda sim: sim.networks.structuredsexual.fsw & ~sim.diseases.hiv.diagnosed,
)

# Lower testing rate for the general population
gp_test = sti.HIVTest(
    test_prob_data=0.05,
    start=2000,
    name='gp_test',
    eligibility=lambda sim: ~sim.networks.structuredsexual.fsw & ~sim.diseases.hiv.diagnosed,
)

art2 = sti.ART(coverage=0.8)

sim = hivsim.demo('simple', run=False, plot=False, n_agents=3000)
sim.pars.interventions = [fsw_test, gp_test, art2]
sim.run(verbose=0)
sim.plot(key=['hiv.prevalence_15_49', 'hiv.new_infections', 'hiv.n_on_art'])


##ART coverage formats and monitoring
# Different coverage formats
art_const = sti.ART(coverage=0.8)                                                     # Constant proportion
art_dict  = sti.ART(coverage={'year': [2000, 2010, 2025], 'value': [0, 0.5, 0.9]})   # Time-varying
art_none  = sti.ART()                                                                  # No target: treat all diagnosed

# Run with the art_coverage analyzer to monitor coverage by age/sex
sim = hivsim.demo('simple', run=False, plot=False, n_agents=5000)
sim.pars.interventions = [sti.HIVTest(test_prob_data=0.3, name='hiv_test'), art_dict]
sim.pars.analyzers = [sti.art_coverage(age_bins=[15, 25, 35, 45, 65])]
sim.run(verbose=0)

# Three ways to inspect the results:

# 1. Use the built-in plot method
sim.analyzers.art_coverage.plot()

# 2. Access results directly
ac = sim.results.art_coverage
print(f'Final overall ART coverage: {ac.p_art[-1]:.1%}')
print(f'Final coverage, women 25-35: {ac.p_art_f_25_35[-1]:.1%}')
print(f'Final coverage, men 25-35:   {ac.p_art_m_25_35[-1]:.1%}')

# 3. Export to a DataFrame for further analysis
df = sim.results.art_coverage.to_df()
print(f'\nDataFrame shape: {df.shape}')
df.head()