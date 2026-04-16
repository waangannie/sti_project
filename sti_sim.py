import stisim as sti

sim = sti.Sim(diseases='ng')
sim.run(verbose=0)
sim.plot(key=['ng.new_infections', 'ng.prevalence'])

sim = sti.Sim(diseases='ng')
sim.init()

print(f'Start:    {sim.pars.start}')
print(f'Stop:     {sim.pars.stop}')
print(f'Timestep: {sim.pars.dt} years ({sim.pars.dt*12:.0f} month)')
print(f'Agents:   {sim.pars.n_agents}')