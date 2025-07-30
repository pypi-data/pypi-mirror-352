# boreholeio

A [Python](https://www.python.org/) library for interacting with [borehole.io](https://borehole.io/), a subsurface data management, delivery and visualisation platform developed by [ALT](https://www.alt.lu/).

> [!CAUTION]
> This package is not yet ready for general consumption. If you'd like more information or to get involved in the development, please get in touch.

## Getting Started

Python developers can install the [boreholeio](https://pypi.org/project/boreholeio) package using [pip](https://pip.pypa.io/en/stable/). From the command line, run `pip install boreholeio` to pull the package into your current Python environment.

The package contains an API client and functionality to interact with data using standard scientific data libraries such as [NumPy](https://numpy.org/), [SciPy](https://scipy.org/) and [Matplotlib](https://matplotlib.org/).

```python
import boreholeio as bio
import matplotlib.pyplot as plt
import itertools

client_settings = bio.JsonClientSettings('~/borehole.io_client.json')
client = bio.Client(client_settings)

# Find ABI logging runs close to ALT HQ
logging_runs = client.logging_runs(
    filter={
        "tool": "ABI",
        "channel": "Amplitude-MN,TravelTime"
        "near": "49.75844052,5.894923998"
    },
    sort={
        "by": "started"
        "order": "descending"
    }
)

# Create a plot of the first 10 logs
figure = plt.figure()
subplots = figure.subplots(1, 10, sharex=True, sharey=True)
for subplot, run in zip(subplots, itertools.islice(logging_runs, 10)):
    # Plot the amplitude map
    amplitude = run.channels['Amplitude-MN'].data
    subplot.pcolormesh(
        bio.data.helpers.centers_to_edges(amplitude.axes[1].coordinates),
        bio.data.helpers.centers_to_edges(amplitude.axes[0].coordinates),
        amplitude
    )

    # Set the title of each plot to metadata from the logging run
    borehole = (run.borehole or {}).get("name")
    user = (run.device or {}).get("user")
    started = run.started.date().isoformat()
    subplot.set_title(f"{borehole}\n{user}\n{started}")

    # Set axis labels
    subplot.set_xlabel(f"{amplitude.axes[1].name} ({amplitude.axes[1].units})")
    subplot.set_ylabel(f"{amplitude.axes[0].name} ({amplitude.axes[0].units})")
```
