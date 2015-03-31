from matplotlib import pylab as pl
import auction
import sys

def plot_options(x,y, options):
  # plot the figure
  fig = pl.figure()
  pl.plot(reserves, revenues)
  pl.xlabel(options.figure_xlabel)
  pl.ylabel(options.figure_ylabel)
  pl.title(options.figure_title)
  fig.savefig(options.figure_file)


def plot_revenue_by_reserve(args, options, reserves):
  '''
  Runs repeated auctions and plots the revenue of each by varying reserves
  '''
  # calculate revenues for different reserve prices
  revenues = []
  for r in reserves:
    options.reserve = r
    results = auction.run_sim(options, args)
    revenue = float(results['revenue']) / 100
    revenues.append(revenue)

  plot_options(reserves, revenues, options)

def plot_revenue_by_period(args,options):
  '''
  Runs a the auction simulation and plots the revenues for each time period
  '''
  results = auction.run_sim(options, args)
  revenues = results['revenues']

  # now plot
  x = range(0,len(revenues))
  y = revenues

  plot_revenue_by_period(x,y, options)

def parse_figure_inputs(parser):

  parser.add_option("--figure_file",
                    dest="figure_file", default="reserve_plot",
                    help="The name under which the plot is saved.")
  
  parser.add_option("--figure_title",
                    dest="figure_title", default="Revenue to Reserve",
                    help="The title of the plot.")
  
  parser.add_option("--figure_xlabel",
                    dest="figure_xlabel", default="Reserve Price (cents)",
                    help="The label for the x-axis.")
  
  parser.add_option("--figure_ylabel",
                    dest="figure_ylabel", default="Revenue (in dollars)",
                    help="The label for the y-axis.")
  return parser

def parse_reserve_inputs(args):
  parser = auction.parse_inputs(args)

  parser = parse_figure_inputs(parser)

  # add new options
  parser.add_option("--max_reserve",
                    dest="max_reserve", default=0,
                    help="The maximum reserve to try. Must be >= reserve")

  parser.add_option("--reserve_gap",
                    dest="reserve_gap", default=1,
                    help="The gap between each reserve in [reserve, max_reserve). Ignored when not applicable")

  return parser

def parse_inputs(args):
  return parse_reserve_inputs(args)

def main(args):
  # lets parse the inputs as usual
  parser = parse_inputs(args)
  (options, args) = parser.parse_args()

  # plotting periods
  if options.mechanism == "switch":
    plot_revenue_by_period(args, options)

  else:
    max_reserve = int(options.max_reserve)
    reserve_gap = int(options.reserve_gap)
    reserve = int(options.reserve)

    # we want to repeat the auction a few times while capturing the mean revenue
    if max_reserve < reserve + reserve_gap:
      auction.run_sim(options, args)
    else:
      reserves = range(reserve, max_reserve, reserve_gap)
      plot_revenue_by_reserve(args, options, reserves)

if __name__ == '__main__':
  main(sys.argv)
