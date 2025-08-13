import json
import pandas as pd

class FewShotPosts:
    def __init__(self, file_path="data/processed_posts.json"):
        self.df = None
        self.unique_tags = None
        self.load_posts(file_path)
        
    def load_posts(self, file_path):
        with open(file_path, encoding="utf-8") as f:
            posts = json.load(f)
            self.df = pd.json_normalize(posts)
            self.df["length"] = self.df["line_count"].apply(self.categorize_length)
            all_tags = self.df["tags"].apply(lambda x: x if isinstance(x, list) else []).sum()
            self.unique_tags = set(all_tags)
        
    def categorize_length(self, line_count):
        if line_count < 5:
            return "short"
        elif 5 <= line_count <= 10:
            return "medium"
        else:
            return "long"
        
    def get_tags(self):
        return self.unique_tags
        
    def get_filtered_posts(self, length, language, tag):
        df_filtered = self.df[
            (self.df["language"] == language) &
            (self.df["length"] == length) &
            (self.df["tags"].apply(lambda tags: tag in tags))
        ]
        return df_filtered.to_dict(orient="records")
            
if __name__ == "__main__":
    ffs = FewShotPosts()
    posts = ffs.get_filtered_posts("short", "English", "Job Search")
    print(posts)
