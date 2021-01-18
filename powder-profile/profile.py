#!/usr/bin/python

"""
####Packaged profile for RF Propagation validation
Joint work that uses SPLAT! (open-source RF singal propgation, loss and 
terrain analysis tool for the electromagnetic spectrum between 20 MHz
and 20 GHz) and Shout (POWDER team developed RF propagation measurements
tool for the POWDER platform) to promote RF propagation validation.

This profile allows you to: 
1. Instantiate the profile with only compute resources and use the provided
SPLAT! software and POWDER related configuration information to perform RF
propagation predictions.
2. Instantiate the profile to include radio nodes and use the provided Shout 
measurement framework to perform RF measurements.
3. Instantiate the profile with both compute and radio resources. Perform a 
combination of the above two activities.

Instructions:

####For the SPLAT! option
Once the experiment is ready you can make your way to `cd /local/repository/splat` 
here you will find the splat folder. This single compute node gives you 
the ability to perform RF propagation predictions through the use of open
source SPLAT!.

To perform RF propagtion measurements you can also simply run SPLAT! 
commands within the splat directory using: `sudo splat -t <tx.qth> -r <rx.qth> -metric -f <freq in MHz>`
This command produces a report in the form of .txt file and can be 
opened to view all sorts of RF measurments. For more options type the 
command `man splat`

####For the Shout option
The Shout profile allows you to conduct RF measurments on the radio
nodes provided by the POWDER platform. Once you select your radios 
and frequency and your experiment is ready to go you will need:
* Two orchestrator terminals open with x11 forwarding (e.g., -XY when ssh)
* One terminal per radio compute node

Next you want to make sure you run the `sudo bash` command in all the terminal 
windows. Following that you need to:
1. In one orchestrator terminal run the following `tail -f /var/tmp/shout_orchestrator.log`
command this helps you see what nodes have connected and what is going on in the
overall measurement conducted
2. In the other orchestrator terminal run `hostname -I` command. Make sure you save this
IP as it will be used shortly
3. In all radio terminals run `/local/repository/shout/meascli.py -s <Orch IP>` where <Orch IP> 
is the IP address from step 2. This connects the client radios to the orchestrator so that we 
can begin the measurements collection
     * If you don't see green brackets in the radio terminal(s), or have exceptions, please power cycle 
       the radio node(s) in the POWDER web UI dashboard by clicking on the gear and pressing power cycle
     * Feel free to copy and paste any other commands that appear in the radio node terminals after pasting the step 3 command 
4.  Next in the non-busy orchestrator terminal run `cd /local/repository/shout/cmdfiles` or make your way
to this directory. 
     * You want to vim or emacs into the `allpathmeas.json` file and modify `freq` to the one you selected
5. Next in the same orchestrator node from step 4 make your way to `cd /local/repository/shout/`
     * Here you want to run `./measiface.py -c cmdfiles/allpathmeas.json` This command starts the measurement 
      process 
6. You will now see the radio nodes and orchestrator node interacting and performing RF propagation measurements
7. The next step is to go to `cd /local/repository/shout` on the orchestrator node 
     * To get the current data into a graph simply run `./analyze-data.py -a`
     * If you have x11 forwarding setup properly you should see a plot of Shout at the chosen frequency 

####For the Combined option
The Combined profile allows you to conduct RF measurments on the radio
nodes provided by the POWDER platform and do the same measurment run
but using SPLAT! Once you select your radios 
and frequency and the experiment is ready to go you will need:
* Two orchestrator terminals open with x11 forwarding (e.g., -XY when ssh)
* One terminal per radio compute node

Next you want to make sure you run the `sudo bash` command in all the terminal 
windows. Following that you need to:
1. In one orchestrator terminal run the following `tail -f /var/tmp/shout_orchestrator.log`
command this helps you see what nodes have connected and what is going on in the
overall measurement conducted
2. In the other orchestrator terminal run `hostname -I` command. Make sure you save this
IP as it will be used shortly
3. In all radio terminals run `/local/repository/shout/meascli.py -s <Orch IP>` where <Orch IP> 
is the IP address from step 2. This connects the client radios to the orchestrator so that we 
can begin the measurements collection
     * If you don't see green brackets in the radio terminal(s), or have exceptions, please power cycle 
       the radio node(s) in the POWDER web UI dashboard by clicking on the gear and pressing power cycle
     * Feel free to copy and paste any other commands that appear in the radio node terminals after pasting the step 3 command 
4.  Next in the non-busy orchestrator terminal run `cd /local/repository/shout/cmdfiles` or make your way
to this directory. 
     * You want to vim or emacs into the `allpathmeas.json` file and modify `freq` to the one you selected
5. Next in the same orchestrator node from step 4 make your way to `cd /local/repository/shout/`
     * Here you want to run `./measiface.py -c cmdfiles/allpathmeas.json` This command starts the measurement 
      process 
6. You will now see the radio nodes and orchestrator node interacting and performing RF propagation measurements
7. The next step is to go to `cd /local/repository/shout` on the orchestrator node 
     * To get the SPLAT! data and graph simply run `./analyze-data.py -j`
     * You should see SPLAT! working its magic (NOTE: this will take time as you are running another measurements experiment)
     * If you have x11 setup properly you should see a plot of Shout and SPLAT! at the chosen frequency 

"""

# Library imports
import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.emulab.pnext as pn
import geni.rspec.emulab.spectrum as spectrum
import geni.rspec.igext as ig


# Global Variables
meas_disk_image = \
        "urn:publicid:IDN+emulab.net+image+PowderTeam:U18-GR-PBUF"
orch_image = meas_disk_image
x310_node_image = meas_disk_image
nuc_image = meas_disk_image
sm_image = meas_disk_image
splat_image = meas_disk_image
clisetup_cmd = "/local/repository/bin/cli-startup.sh"
orchsetup_cmd = "/local/repository/bin/orch-startup.sh"
orchsetupcombined_cmd = "/local/repository/bin/orch-startup-combined.sh"
splat_cmd = "/local/repository/bin/splat-startup.sh"
per_cmd = "chmod +x /local/repository/bin/splat-startup.sh"
combinedper_cmd = "chmod +x /local/repository/bin/orch-startup-combined.sh"

# Top-level request object.
request = portal.context.makeRequestRSpec()

# Helper function that allocates a PC + X310 radio pair, with Ethernet
# link between them.
def x310_node_pair(x310_radio_name, node_type, orchhost):
    radio_link = request.Link("%s-link" % x310_radio_name)

    node = request.RawPC("%s-comp" % x310_radio_name)
    node.hardware_type = node_type
    node.disk_image = x310_node_image

    node.addService(rspec.Execute(shell="bash",
                                  command=clisetup_cmd + " %s" % orchhost))

    node_radio_if = node.addInterface("usrp_if")
    node_radio_if.addAddress(rspec.IPv4Address("192.168.40.1",
                                               "255.255.255.0"))
    radio_link.addInterface(node_radio_if)

    radio = request.RawPC("%s-x310" % x310_radio_name)
    radio.component_id = x310_radio_name
    radio_link.addNode(radio)

# Profile type to differntiate between simple SPLAT node 
# and full SPLAT + Shout profile combination. 
portal.context.defineParameter(
    "profiletype",
    "Profile Type",
    portal.ParameterType.STRING, "SPLAT!",
    ["SPLAT!","Shout", "Combined"],
    "* SPLAT!: Single compute node with SPLAT! software and POWDER related\
    configuration information to perform RF predictions. No need to select\
    any options below\n\
    * Shout: Includes radio nodes and use the provided Shout measurements\
    framework to perform RF measurements. Select Options below\n\
    * Combined: Profile with both compute and radio resources. Perform a\
    combination of the above two activities. Select options below.",
)

# Node type parameter for PCs to be paired with X310 radios.
# Restricted to those that are known to work well with them.
portal.context.defineParameter(
    "nodetype",
    "Compute node type",
    portal.ParameterType.STRING, "d740",
    ["d740","d430"],
    "Type of compute node to be paired with the X310 Radios.\n\
    Only use for Shout or Combined profiles",
)

# Node type for the orchestrator.
portal.context.defineParameter(
    "orchtype",
    "Orchestrator node type",
    portal.ParameterType.STRING, "",
    ["", "d430","d740"],
    "Type of compute node for the orchestrator (unset == 'any available')\n\
    Only use for Shout or Combined profiles",
)

# List of CBRS rooftop X310 radios.
cbrs_radios = [
    ("cbrssdr1-bes",
     "Behavioral"),
    ("cbrssdr1-browning",
     "Browning"),
    ("cbrssdr1-dentistry",
     "Dentistry"),
    ("cbrssdr1-fm",
     "Friendship Manor"),
    ("cbrssdr1-hospital",
     "Hospital"),
    ("cbrssdr1-honors",
     "Honors"),
    ("cbrssdr1-meb",
     "MEB"),
    ("cbrssdr1-smt",
     "SMT"),
    ("cbrssdr1-ustar",
     "USTAR"),
]

# List of Cellular radios
cell_radios = [
    ("cellsdr1-bes",
     "Behavioral"),
    ("cellsdr1-browning",
     "Browning"),
    ("cellsdr1-dentistry",
     "Dentistry"),
    ("cellsdr1-fm",
     "Friendship Manor"),
    ("cellsdr1-hospital",
     "Hospital"),
    ("cellsdr1-honors",
     "Honors"),
    ("cellsdr1-meb",
     "MEB"),
    ("cellsdr1-smt",
     "SMT"),
    ("cellsdr1-ustar",
     "USTAR"),
]

# A list of fixed endpoint sites.
fe_sites = [
    ('urn:publicid:IDN+bookstore.powderwireless.net+authority+cm',
     "Bookstore"),
    ('urn:publicid:IDN+cpg.powderwireless.net+authority+cm',
     "Garage"),
    ('urn:publicid:IDN+ebc.powderwireless.net+authority+cm',
     "EBC"),
    ('urn:publicid:IDN+guesthouse.powderwireless.net+authority+cm',
     "GuestHouse"),
    ('urn:publicid:IDN+humanities.powderwireless.net+authority+cm',
     "Humanities"),
    ('urn:publicid:IDN+law73.powderwireless.net+authority+cm',
     "Law73"),
    ('urn:publicid:IDN+madsen.powderwireless.net+authority+cm',
     "Madsen"),
    ('urn:publicid:IDN+moran.powderwireless.net+authority+cm',
     "Moran"),
    ('urn:publicid:IDN+sagepoint.powderwireless.net+authority+cm',
     "SagePoint"),
    ('urn:publicid:IDN+web.powderwireless.net+authority+cm',
     "WEB"),
]

# A list of mobile endpoint sites.
me_sites = [
    ("urn:publicid:IDN+bus-4964.powderwireless.net+authority+cm",
     "Bus4964"),
    ("urn:publicid:IDN+bus-6185.powderwireless.net+authority+cm",
     "Bus6185"),
]

# Set of CBRS X310 radios to allocate
portal.context.defineStructParameter(
    "cbrs_radio_sites", "CBRS Radio Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="CBRS X310 radios to allocate.",
    members=[
        portal.Parameter(
            "radio",
            "CBRS Radio Site",
            portal.ParameterType.STRING,
            cbrs_radios[0], cbrs_radios,
            longDescription="CBRS X310 radio will be allocated from selected site."
        ),
    ])

# Set of Cellular X310 radios to allocate
portal.context.defineStructParameter(
    "cell_radio_sites", "Cellular Radio Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="Cellular X310 radios to allocate.",
    members=[
        portal.Parameter(
            "radio",
            "Cellular Radio Site",
            portal.ParameterType.STRING,
            cell_radios[0], cell_radios,
            longDescription="Cellular X310 radio will be allocated from selected site."
        ),
    ])

# Set of Fixed Endpoint devices to allocate
portal.context.defineStructParameter(
    "fe_radio_sites", "Fixed Endpoint Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="Fixed Endpoint NUC+B210 radios to allocate.",
    members=[
        portal.Parameter(
            "site",
            "FE Site",
            portal.ParameterType.STRING,
            fe_sites[0], fe_sites,
            longDescription="A `nuc2` device will be selected at the site."
        ),
    ])

# Set of Mobile Endpoint devices to allocate
portal.context.defineStructParameter(
    "me_radio_sites", "Mobile Endpoint Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="Mobile Endpoint Supermicro+B210 radios to allocate.",
    members=[
        portal.Parameter(
            "site",
            "ME Site",
            portal.ParameterType.STRING,
            me_sites[0], me_sites,
            longDescription="An `ed1` device will be selected at the site."
        ),
    ])

# Frequency/spectrum parameters
portal.context.defineStructParameter(
    "cbrs_freq_ranges", "CBRS Frequency Ranges", [],
    multiValue=True,
    min=0,
    multiValueTitle="Frequency ranges for CBRS operation.",
    members=[
        portal.Parameter(
            "freq_min",
            "Frequency Min",
            portal.ParameterType.BANDWIDTH,
            3550.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Frequency Max",
            portal.ParameterType.BANDWIDTH,
            3560.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ])

portal.context.defineStructParameter(
    "b7_freq_ranges", "Band 7 Frequency Ranges", [],
    multiValue=True,
    min=0,
    multiValueTitle="Frequency ranges for Band 7 cellular operation.",
    members=[
        portal.Parameter(
            "ul_freq_min",
            "Uplink Frequency Min",
            portal.ParameterType.BANDWIDTH,
            2500.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "ul_freq_max",
            "Uplink Frequency Max",
            portal.ParameterType.BANDWIDTH,
            2510.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "dl_freq_min",
            "Downlink Frequency Min",
            portal.ParameterType.BANDWIDTH,
            2620.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "dl_freq_max",
            "Downlink Frequency Max",
            portal.ParameterType.BANDWIDTH,
            2630.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ])

# Bind and verify parameters
params = portal.context.bindParameters()

# Determine which profile to create 
if params.profiletype == "SPLAT!":
    # Single SPLAT NODE
    splat = request.RawPC("splat")
    splat.disk_image = splat_image
    splat.addService(rspec.Execute(shell="bash", command=per_cmd))
    splat.addService(rspec.Execute(shell="bash", command=splat_cmd))
else:
    # Full Shout Profile 
    for i, frange in enumerate(params.cbrs_freq_ranges):
        if frange.freq_min < 3400 or frange.freq_min > 3800 \
        or frange.freq_max < 3400 or frange.freq_max > 3800:
            perr = portal.ParameterError("CBRS frequencies must be between 3400 and 3800 MHz", ["cbrs_freq_ranges[%d].freq_min" % i, "cbrs_freq_ranges[%d].freq_max" % i])
            portal.context.reportError(perr)
        if frange.freq_max - frange.freq_min < 1:
            perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["cbrs_freq_ranges[%d].freq_min" % i, "cbrs_freq_ranges[%d].freq_max" % i])
            portal.context.reportError(perr)

    for i, frange in enumerate(params.b7_freq_ranges):
        if frange.ul_freq_min < 2500 or frange.ul_freq_min > 2570 \
        or frange.ul_freq_max < 2500 or frange.ul_freq_max > 2570:
            perr = portal.ParameterError("Band 7 uplink frequencies must be between 2500 and 2570 MHz", ["b7_freq_ranges[%d].ul_freq_min" % i, "b7_freq_ranges[%d].ul_freq_max" % i])
            portal.context.reportError(perr)
        if frange.ul_freq_max - frange.ul_freq_min < 1:
            perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["b7_freq_ranges[%d].ul_freq_min" % i, "b7_freq_ranges[%d].ul_freq_max" % i])
            portal.context.reportError(perr)
        if frange.dl_freq_min < 2620 or frange.dl_freq_min > 2690 \
        or frange.dl_freq_max < 2620 or frange.dl_freq_max > 2690:
            perr = portal.ParameterError("Band 7 downlink frequencies must be between 2620 and 2690 MHz", ["b7_freq_ranges[%d].dl_freq_min" % i, "b7_freq_ranges[%d].dl_freq_max" % i])
            portal.context.reportError(perr)
        if frange.dl_freq_max - frange.dl_freq_min < 1:
            perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["b7_freq_ranges[%d].dl_freq_min" % i, "b7_freq_ranges[%d].dl_freq_max" % i])
            portal.context.reportError(perr)

    # Now verify.
    portal.context.verifyParameters()

    # Differentiation from normal Shout and Combined Profile
    if params.profiletype == "Shout":
        # Allocate orchestrator node
        orch = request.RawPC("orch")
        orch.disk_image = orch_image
        orch.hardware_type = params.orchtype
        orch.addService(rspec.Execute(shell="bash", command=orchsetup_cmd))
    else:
        # Allocate orchestrator node
        orch = request.RawPC("orch")
        orch.disk_image = orch_image
        orch.hardware_type = params.orchtype
        orch.addService(rspec.Execute(shell="bash", command=combinedper_cmd))
        orch.addService(rspec.Execute(shell="bash", command=orchsetupcombined_cmd))

    # Request PC + CBRS X310 resource pairs.
    for rsite in params.cbrs_radio_sites:
        x310_node_pair(rsite.radio, params.nodetype, orch.name)

    # Request PC + Cellular X310 resource pairs.
    for rsite in params.cell_radio_sites:
        x310_node_pair(rsite.radio, params.nodetype, orch.name)

    # Request nuc2+B210 radio resources at FE sites.
    for fesite in params.fe_radio_sites:
        nuc = ""
        for urn,sname in fe_sites:
            if urn == fesite.site:
                nuc = request.RawPC("%s-b210" % sname)
                break
        nuc.component_manager_id = fesite.site
        nuc.component_id = "nuc2"
        nuc.disk_image = nuc_image
        nuc.addService(rspec.Execute(shell="bash", command=clisetup_cmd))

    # Request ed1+B210 radio resources at ME sites.
    for mesite in params.me_radio_sites:
        node = ""
        for urn,sname in me_sites:
            if urn == mesite.site:
                node = request.RawPC("%s-b210" % sname)
                break
        node.component_manager_id = mesite.site
        node.component_id = "ed1"
        node.disk_image = sm_image
        node.addService(rspec.Execute(shell="bash", command=clisetup_cmd))
        
    # Request frequency range(s)
    for frange in params.cbrs_freq_ranges:
        request.requestSpectrum(frange.freq_min, frange.freq_max, 0)

    for frange in params.b7_freq_ranges:
        request.requestSpectrum(frange.ul_freq_min, frange.ul_freq_max, 0)
        request.requestSpectrum(frange.dl_freq_min, frange.dl_freq_max, 0)
    
# Emit!
portal.context.printRequestRSpec()
