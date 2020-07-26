import os
import numpy as np
import matplotlib.pyplot as plt
import argparse

def main(args):
	os.makedirs(args.output, exist_ok=True)

	txt_files = os.listdir(args.input)
	txt_files = list(filter(lambda x: x.endswith(".txt"), txt_files))

	best_sde_values = []
	ts = [x for x in range(0, 255) if x % 10 == 0]
	ps = [x for x in range(11)] + [x for x in range(20, 101) if x % 10 == 0]

	plt.figure(figsize=(16, 9), dpi=250)
	for t in ts:
		sde_values = []
		
		best_value = (np.inf, 0)
		for p in ps:
			filename = f"t_{t}__p_{p}.txt"
			path = os.path.join(args.input, filename)
			with open(path, "r") as result_file:
				for line in result_file:
					if line and line.startswith("sde mean:"):
						value = float(line.split(":")[1].lstrip().rstrip())
						sde_values.append(value)

						if value < best_value[0]:
							best_value = (value, p)
		best_sde_values.append(best_value)

		plt.plot(ps, sde_values)
		plt.xticks(ps)
		plt.title(rf"$\tau={t}$, $\phi='{args.name}'$")
		plt.xlabel(r"Pruning Percentage $\pi$")
		plt.ylabel("Average SDE")
		plt.tight_layout()
		plt.savefig(os.path.join(args.output, f"t_{t}.png"))
		plt.savefig(os.path.join(args.output, f"t_{t}.pdf"))
		plt.clf()
		with open(os.path.join(args.output, f"t_{t}.csv"), "w") as csv_out:
			csv_out.write("P,SDE Value\n")
			for p, value in zip(ps, sde_values):
				csv_out.write(f"{p},{value}\n")

	plt.plot(ts, [x[0] for x in best_sde_values])
	plt.xticks(ts)
	plt.title(rf"$\phi='{args.name}'$")
	plt.xlabel(r"Threshold $\tau$")
	plt.ylabel("Average SDE")
	plt.tight_layout()
	plt.savefig(os.path.join(args.output, "overview.png"))
	plt.savefig(os.path.join(args.output, "overview.pdf"))
	plt.clf()
	with open(os.path.join(args.output, "overview.csv"), "w") as csv_out:
		csv_out.write("T,P,Best SDE Value\n")
		for t, (value, p) in zip(ts, best_sde_values):
			csv_out.write(f"{t},{p},{value}\n")


if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument("-i", "--input", type=str, help="Top level folder of aggregated results in .txt files.")
	parser.add_argument("-n", "--name", type=str, help="Name of the edge creation method (phi).")
	parser.add_argument("-o", "--output", type=str, help="Destination folder for plots and results.")

	args = parser.parse_args()

	main(args)
