import os 
import pandas
import numpy as np
import argparse

num_subjects = 1

def main(args):
	os.makedirs(args.output, exist_ok=True)

	ts = [x for x in range(0, 255) if x % 10 == 0]
	ps = [x for x in range(11)] + [x for x in range(20, 101) if x % 10 == 0]

	total = len(ts) * len(ps)
	count = 0
	for t in ts:
		for p in ps:
			print(f"\r{count + 1}/{total}", end="")
			count += 1
			csv_name = f"t_{t}__p_{p}.csv"

			full_path = os.path.join(args.input, csv_name)
			if not os.path.exists(full_path):
				print(f"WARNING: {csv_name} does not exist!")
				continue

			df = pandas.read_csv(full_path, sep=",")

			num_null = 0
			for x in range(args.num_subjects):
				num_null = max(num_null, len(df) - df[f"precision_{x}"].count())

			partial_mean = []
			partial_median = []
			for x in range(args.num_subjects):
				partial_mean.append(df[f"precision_{x}"].mean())
				partial_mean.append(df[f"recall_{x}"].mean())
				partial_mean.append(df[f"sde_{x}"].mean())
				partial_mean.append(df[f"bbiou_{x}"].mean())

				partial_median.append(df[f"precision_{x}"].median())
				partial_median.append(df[f"recall_{x}"].median())
				partial_median.append(df[f"sde_{x}"].median())
				partial_median.append(df[f"bbiou_{x}"].median())
				for y in [0, 5, 10, 15, 20]:
					partial_mean.append(df[f"iou_{y}_{x}"].mean())
					partial_median.append(df[f"iou_{y}_{x}"].median())

			partial_mean = np.asarray(partial_mean)
			partial_median = np.asarray(partial_median)
			# partial_mean = np.reshape(partial_mean, (4 + 5, 7), order="F")
			# partial_median = np.reshape(partial_median, (4 + 5, 7), order="F")

			partial_mean = np.reshape(partial_mean, (4 + 5, args.num_subjects), order="F")
			partial_median = np.reshape(partial_median, (4 + 5, args.num_subjects), order="F")

			reduced_mean = np.mean(partial_mean, axis=-1)
			reduced_median = np.mean(partial_median, axis=-1)

			columns_sde = []
			columns_bbiou = []
			for i in range(args.num_subjects):
				columns_sde.append(f"sde_{i}")
				columns_bbiou.append(f"bbiou_{i}")

			std_sde = df[columns_sde].mean(axis=1).std()
			std_bbiou = df[columns_bbiou].mean(axis=1).std()

			with open(os.path.join(args.output, csv_name.split(".")[0] + ".txt"), "w") as csv_out:
				csv_out.write(f"number of empty images: {num_null}\n")
				csv_out.write("\n")
				csv_out.write(f"precision mean: {reduced_mean[0]}\n")
				csv_out.write(f"precision median: {reduced_median[0]}\n")
				csv_out.write("\n")
				csv_out.write(f"recall mean: {reduced_mean[1]}\n")
				csv_out.write(f"recall median: {reduced_median[1]}\n")
				csv_out.write("\n")
				csv_out.write(f"sde mean: {reduced_mean[2]}\n")
				csv_out.write(f"sde median: {reduced_median[2]}\n")
				csv_out.write(f"sde std: {std_sde}\n")
				csv_out.write("\n")
				csv_out.write(f"bbiou mean: {reduced_mean[3]}\n")
				csv_out.write(f"bbiou median: {reduced_median[3]}\n")
				csv_out.write(f"bbiou std: {std_bbiou}\n")
				csv_out.write("\n")
				for i, y in enumerate([0, 5, 10, 15, 20]):
					csv_out.write(f"iou {y} mean: {reduced_mean[4 + i]}\n")
					csv_out.write(f"iou {y} median: {reduced_median[4 + i]}\n")
					csv_out.write("\n")

if __name__ == "__main__":
	parser = argparse.ArgumentParser()

	parser.add_argument("-i", "--input", type=str, help="Folder containing evaluation csv files.")
	parser.add_argument("-o", "--output", type=str, help="Destination folder for aggregated results.")

	parser.add_argument("-n", "--num_subjects", type=int, help="Number of subjects that evaluated the ground truth data.")

	args = parser.parse_args()

	main(args)
