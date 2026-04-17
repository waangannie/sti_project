import matplotlib.pyplot as plt
import starsim as ss
import stisim as sti

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
plt.show()