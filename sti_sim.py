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