import pandas as pd

# set input and output file names
inputfile = "./csv/document2topics.csv"
output_csv = "./csv/topicswithKeywords.csv"

# read the CSV file
df = pd.read_csv(inputfile, delimiter=",")

# extract unique values of Topic, Name, Top_n_words based on Topic
df_unique = df.groupby("Topic").agg({"Name": pd.Series.unique,
                                      "Top_n_words": pd.Series.unique}).reset_index()

# sort the dataframe by Topic in ascending order
df_unique_sorted = df_unique.sort_values("Topic", ascending=True)


# save the dataframe to a CSV file
df_unique_sorted.to_csv(output_csv, index=False)
