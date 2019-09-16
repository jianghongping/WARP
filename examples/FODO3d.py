"""Basic 3D simulation of an ion beam in a periodic FODO lattice.
This input file sets up a periodic FODO lattice and creates a beam
that is matched to the lattice. The beam is propagated one lattice period.
"""
# --- This imports the Warp code into python, giving access to all
# --- of the Warp data and routines. This is typically the first command
# --- of a Warp input file.
import warp as wp

# --- Setup the description text which will be included at the bottom
# --- of every plot frame. This is for user convenience, documenting
# --- what the simulation is on the graphical output.
wp.top.pline2   = "Example 3D beam in a FODO lattice"
wp.top.pline1   = "Semi-Gaussian cigar beam. 32x32x128"
wp.top.runmaker = "David P. Grote"

# --- Invoke plotting setup routine - it is needed to create a cgm output file for plots.
# --- The plot file will have a name with the format FODO3D.###.cgm. The prefix is the
# --- same as the input file name, and the ### is a number, increasing each time the
# --- simulation is carried out.
wp.setup()

# --- Create the beam species. This instance of the Species class
# --- is used to configure aspects related to the beam and particles.
beam = wp.Species(type=wp.Potassium, charge_state=+1, name="Beam species")

# --- Set input parameters describing the beam, with a tune depression of 72 to 20 degrees.
# --- These numbers were generated by hand, by using the env package and adjusting the
# --- parameters to get the desired results.
# --- Note the units multipliers, e.g. mm. Almost all variables are MKS units
# --- (except ekin). The multipliers provide a nice way of converting to MKS
# --- while providing documentation about the units that are being used.
beam.a0    = 8.760439903086566*wp.mm
beam.b0    = 15.599886448447793*wp.mm
beam.emit  = 6.247186343204832e-05
beam.ap0   = 0.
beam.bp0   = 0.
beam.ibeam = 2.*wp.mA
beam.vbeam = 0.
beam.ekin  = 80.*wp.kV

# --- This call does some further processing on the input parameters.
# --- For example, in the above, the beam energy is specified. derivqty
# --- will calculate the beam velocity from the energy. It is not necessary
# --- to call derivqty (since it will be called during the generate), but it
# --- is called here to calculate beam.vbeam which is used in the calculation
# --- of the longitudinal thermal velocity spread below.
wp.derivqty()

# --- Specify the longitudinal thermal velocity spread. In this case, it
# --- is the same as the transverse thermal velocity spread, as set by
# --- the emittance.
beam.vthz = 0.5*beam.vbeam*beam.emit/wp.sqrt(beam.a0*beam.b0)

# --- Setup the FODO lattice
# --- These are user created python variables describing the lattice.
hlp     = 36.*wp.cm    # half lattice period length
piperad = 3.445*wp.cm  # pipe radius
quadlen = 11.*wp.cm    # quadrupole length

# --- Magnetic quadrupole field gradient - calculated to give sigma0 = 72 degrees.
dbdx = 0.93230106124518164/quadlen

# --- Set up the quadrupoles. Only one lattice period is defined.
# --- This period is repeated to fill all space.
# --- The lattice consists of two quadrupoles, one defocusing, one focusing.
wp.addnewquad(zs=0.5*hlp - quadlen/2.,
              ze=0.5*hlp + quadlen/2.,
              db=+dbdx)
wp.addnewquad(zs=1.5*hlp - quadlen/2.,
              ze=1.5*hlp + quadlen/2.,
              db=-dbdx)

# --- zlatstrt is the start of the periodicity, relative to the quadrupoles position.
wp.top.zlatstrt = 0.

# --- zlatperi is the length of the lattice period, the length of the periodic repeat.
wp.top.zlatperi = 2.0*hlp

# ------------------------------------------------------------------------
# --- The next section sets up and run the envelope equation solver.
# --- Given the initial conditions specified above (a0, b0 etc.),
# --- the envelope package solves the KV envelope equations.
# --- The envelope solution will be used to specify the transverse
# --- shape of the beam where simulation particles will be loaded.

# --- The lattice period length, used to calculate phase advances.
wp.top.tunelen = 2.*hlp

# --- The start and end of the envelope calculation. The initial conditions
# --- are the values at env.zl. Note that zl and zu must cover
# --- the longitudinal extent where the beam particles will be loaded.
# --- dzenv is the step size used in the envelope solver.
wp.env.zl    = -2.5*hlp  # z-lower
wp.env.zu    = -wp.env.zl  # z-upper
wp.env.dzenv = wp.top.tunelen/100.

# --- Select the envelope solver, do any initialization, and solve the equations.
wp.package("env")
wp.generate()
wp.step()

# --- Make a plot of the resulting envelope solution.
wp.penv()
wp.fma()

# ------------------------------------------------------------------------
# --- Now, set up the parameters describing the 3D simulation.

# --- Specify the time step size. In this case, it is set so that
# --- it takes the specified number of time steps per lattice period.
steps_p_perd = 50
wp.top.dt = (wp.top.tunelen/steps_p_perd)/beam.vbeam

# --- Specify the number of grid cells in each dimension.
wp.w3d.nx = 32
wp.w3d.ny = 32
wp.w3d.nz = 128

# --- Specify the extent of the field solve grid.
wp.w3d.xmmin = -piperad
wp.w3d.xmmax = piperad
wp.w3d.ymmin = -piperad
wp.w3d.ymmax = piperad
wp.w3d.zmmin = -hlp*2
wp.w3d.zmmax = +hlp*2

# --- Specify the boundary conditions on the outer sides of the grid.
# --- Possible values are dirichlet, periodic, and neumann.
wp.w3d.bound0  = wp.dirichlet  # at iz == 0
wp.w3d.boundnz = wp.dirichlet  # at iz == nz
wp.w3d.boundxy = wp.dirichlet  # at all transverse sides

# --- Set the particle boundary conditions at the outer sides of the grid.
# --- Possible values are absorb, periodic, and reflect.
wp.top.pbound0  = wp.absorb
wp.top.pboundnz = wp.absorb
wp.top.pboundxy = wp.absorb

# --- Set the beam pulse length.
# --- Here, it is set to 80% of the grid length.
beam.zimin = wp.w3d.zmmin*0.8
beam.zimax = wp.w3d.zmmax*0.8

# --- Setup the parameters describing how the beam is created.
# --- npmax is the number of simulation particles to create.
wp.top.npmax = 200000

# --- The distribution of the beam.
# --- There are a number of possible values, including "semigauss", "KV", and "WB".
wp.w3d.distrbtn = "semigaus"

# --- The longitudinal velocity distribution of the beam.
wp.w3d.distr_l = "gaussian"

# --- Turn on the "cigar" loading option This imposes a parabolic taper in the line-charge
# --- at the ends of the beam, adjusting the beam envelope to stay matched.
# --- beam.straight specifies the fraction of the beam that is in the middle, without the tapering.
# --- The length of each end will be (1 - beam.straight)/2.
wp.w3d.cigarld = True
beam.straight = 0.5

# --- Set up field solver.
# --- fstype == 0 species the FFT solver.
wp.top.fstype = 0

# --- Optional symmetries can be imposed on the solver.
# --- If l4symtry is true, the fields are calculated in only in transverse
# --- quadrant, and are replicated in the other quadrants.
# --- Note that the particles still occupy all of transverse space.
# --- When the charge is deposited, it would be mapped into the one quadrant.
wp.w3d.l4symtry = False

# --- Setup various diagnostics and plots.
# --- By default, Warp calculates all 1st and 2nd order moments of the particles
# --- as a function of z position.

# --- Warp can save histories of the values of these moments at a selected number
# --- of z-locations relative to the beam frame. These locations are specified
# --- by zwindows. Note that the moments at the center of the window are saved.
# --- The zwindows are given a finite extent since that can also be used to
# --- select particles within the range, for plotting for example.
# --- Note that top.zwindows[:,0] always includes the whole longitudinal extent
# --- and should not be changed.
wp.top.zwindows[:, 1] = [-0.35, -0.3]
wp.top.zwindows[:, 2] = [-0.25, 0.25]
wp.top.zwindows[:, 3] = [0.3, 0.35]

# --- Since it can use a significant amount of memory, only time histories of the
# --- line-charge and vzbar are saved by default. These lines turn on the saving
# --- of time histories of other quantities.
wp.top.lhxrmsz  = True
wp.top.lhyrmsz  = True
wp.top.lhepsnxz = True
wp.top.lhepsnyz = True
wp.top.lhcurrz  = True

# --- nhist specifies the period, in time steps, of saving histories of
# --- the particle moments.
wp.top.nhist = 1

# --- Define some plots to make and the frequency.
# --- zzplalways defines how often certain plots are generated.
# --- zzplalways = [zstart, zend, zperiod, extra_z_values, ...]
wp.top.zzplalways[0:4] = [0., 100000., 2*hlp, 0.]

# --- These specify that the plots ppzxy and ppzvz will be called as specified by zzplalways.
wp.top.ipzxy[-2] = wp.always
wp.top.ipzvz[-2] = wp.always

# --- User defined functions can be called from various points within the time step loop.
# --- This "@callfromafterstep" is a python decorator that says that this function will
# --- be called after every time step.


@wp.callfromafterstep
def runtimeplots(nsteps=steps_p_perd):
    "Make user defined plots, every steps_p_perd steps"
    if wp.top.it % nsteps != 0:
        return
    # --- Create overlaid plots in subframes of the plot window.
    wp.plsys(9)
    wp.pfzx(cellarray=1, contours=0, centering='cell')
    wp.pzxedges(color=wp.red, titles=False)
    wp.plsys(10)
    wp.pfzy(cellarray=1, contours=0, centering='cell')
    wp.pzyedges(color=wp.red, titles=False)
    wp.fma()

    # --- Make plots of the transverse distribution in two zwindows.
    wp.plsys(3)
    wp.ppxy(iw=1)
    wp.limits(-0.02, +0.02, -0.02, +0.02)
    wp.plsys(4)
    wp.ppxxp(iw=1)
    wp.limits(-0.02, +0.02, -0.04, +0.04)
    wp.plsys(5)
    wp.ppxy(iw=3)
    wp.limits(-0.02, +0.02, -0.02, +0.02)
    wp.plsys(6)
    wp.ppxxp(iw=3)
    wp.limits(-0.02, +0.02, -0.04, +0.04)
    wp.fma()


# --- Switch to the w3d package, which runs the 3D PIC model.
# --- The generate command does the initialization, including creating
# --- the particles, doing the initial Poisson solve, and calculating
# --- initial diagnostics and moments.
wp.package("w3d")
wp.generate()

# --- Directly call the user defined function, producing plots of the initial conditions.
runtimeplots()

# --- Run for 50 time steps.
# --- Note that after each time step, the routine runtimeplots will be automatically called.
wp.step(50)

# --- Make various post processing diagnostic plots.
wp.ptitles('Beam X envelope history, in beam frame', 'Lattice periods',
           'Beam frame location (m)', 'Envelope is 2*Xrms')
wp.ppgeneric(gridt=2.*wp.top.hxrmsz[:, :wp.top.jhist, 0], xmin=0.,
             xmax=wp.top.zbeam/(2.*hlp), ymin=wp.w3d.zmmin, ymax=wp.w3d.zmmax)
wp.fma()

wp.ptitles('Beam X normalized emittance history, in beam frame', 'Lattice periods', 'Beam frame location (m)')
wp.ppgeneric(gridt=wp.top.hepsnxz[:, :wp.top.jhist, 0], xmin=0.,
             xmax=wp.top.zbeam/(2.*hlp), ymin=wp.w3d.zmmin, ymax=wp.w3d.zmmax)
wp.fma()

wp.hpepsnx()
wp.hpepsny(titles=0)
wp.fma()