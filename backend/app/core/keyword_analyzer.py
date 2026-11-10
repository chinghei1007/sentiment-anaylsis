"""
Keyword-Based Sentiment Analysis
Analyzes sentiment at the keyword/phrase level within text
"""

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    col, 
    udf, 
    explode, 
    split, 
    lower, 
    regexp_replace,
    trim,
    lit,
    when,
    count,
    sum as spark_sum,
    avg as spark_avg
)
from pyspark.sql.types import (
    StringType, 
    ArrayType, 
    DoubleType, 
    IntegerType,
    StructType,
    StructField
)
from pyspark.ml.feature import (
    Tokenizer,
    StopWordsRemover,
    NGram
)
import re
import logging
from typing import Dict, List, Optional, Any, Tuple
from collections import Counter
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

logger = logging.getLogger(__name__)

# Download NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
except:
    pass


class KeywordSentimentAnalyzer:
    """
    Analyzes sentiment at the keyword level
    Extracts keywords, calculates sentiment scores, and identifies trends
    """
    
    def __init__(self, spark: Optional[SparkSession] = None):
        """
        Initialize keyword analyzer
        
        Args:
            spark: SparkSession instance (created if None)
        """
        self.spark = spark or SparkSession.builder \
            .appName("KeywordSentimentAnalyzer") \
            .getOrCreate()
        
        self.stop_words = set(stopwords.words('english'))
        self.lemmatizer = WordNetLemmatizer()
        
        # Sentiment lexicons
        self.positive_words = self._load_sentiment_lexicon("positive")
        self.negative_words = self._load_sentiment_lexicon("negative")
        
        # Custom keyword weights
        self.keyword_weights: Dict[str, float] = {}
        
    def _load_sentiment_lexicon(self, sentiment: str) -> set:
        """Load default sentiment lexicon"""
        # Basic sentiment word lists
        positive_list = [
            "good", "great", "excellent", "amazing", "wonderful", "fantastic",
            "love", "like", "best", "awesome", "perfect", "happy", "satisfied",
            "impressed", "recommend", "quality", "beautiful", "superb", "outstanding",
            "positive", "pleased", "delighted", "thrilled", "excellent"
        ]
        
        negative_list = [
            "bad", "terrible", "awful", "horrible", "worst", "poor",
            "hate", "dislike", "disappointed", "waste", "garbage", "scam",
            "broken", "damaged", "refund", "complain", "issue", "problem",
            "negative", "unhappy", "angry", "frustrated", "disgusting"
        ]
        
        if sentiment == "positive":
            return set(positive_list)
        elif sentiment == "negative":
            return set(negative_list)
        else:
            return set()
    
    def add_custom_keywords(self, keywords: Dict[str, float]) -> None:
        """
        Add custom keywords with sentiment weights
        
        Args:
            keywords: Dictionary of {keyword: sentiment_score}
                     Score > 0 = positive, < 0 = negative
        """
        self.keyword_weights.update(keywords)
        logger.info(f"Added {len(keywords)} custom keywords")
    
    def extract_keywords(
        self,
        df: DataFrame,
        text_column: str = "text",
        min_length: int = 3,
        max_length: int = 20,
        ngram_range: Tuple[int, int] = (1, 2)
    ) -> DataFrame:
        """
        Extract keywords from text data
        
        Args:
            df: Input DataFrame
            text_column: Column containing text
            min_length: Minimum keyword length
            max_length: Maximum keyword length
            ngram_range: Range of n-grams to extract (e.g., (1, 2) for unigrams and bigrams)
            
        Returns:
            DataFrame with extracted keywords
        """
        # Clean text
        df = df.withColumn(
            "clean_text",
            regexp_replace(lower(col(text_column)), r'[^a-z\s]', ' ')
        )
        
        # Tokenize
        tokenizer = Tokenizer(inputCol="clean_text", outputCol="tokens")
        df = tokenizer.transform(df)
        
        # Remove stop words
        remover = StopWordsRemover(
            inputCol="tokens",
            outputCol="filtered_tokens",
            stopWords=list(self.stop_words)
        )
        df = remover.transform(df)
        
        # Extract n-grams
        if ngram_range[1] > 1:
            ngram = NGram(
                n=ngram_range[1],
                inputCol="filtered_tokens",
                outputCol="ngrams"
            )
            df = ngram.transform(df)
            
            # Combine tokens and n-grams
            df = df.withColumn(
                "all_phrases",
                udf(lambda tokens, ngrams: tokens + ngrams, ArrayType(StringType()))(
                    col("filtered_tokens"),
                    col("ngrams")
                )
            )
        else:
            df = df.withColumn("all_phrases", col("filtered_tokens"))
        
        # Explode phrases
        df = df.withColumn("keyword", explode(col("all_phrases")))
        
        # Filter by length
        df = df.withColumn(
            "keyword",
            when(
                (length(col("keyword")) >= min_length) & 
                (length(col("keyword")) <= max_length),
                col("keyword")
            ).otherwise(None)
        )
        df = df.filter(col("keyword").isNotNull())
        
        return df
    
    def calculate_keyword_sentiment(self, keyword: str) -> float:
        """
        Calculate sentiment score for a single keyword
        
        Args:
            keyword: Keyword to analyze
            
        Returns:
            Sentiment score (-1 to 1)
        """
        keyword_lower = keyword.lower()
        
        # Check custom weights first
        if keyword_lower in self.keyword_weights:
            return self.keyword_weights[keyword_lower]
        
        # Check lexicons
        if keyword_lower in self.positive_words:
            return 1.0
        elif keyword_lower in self.negative_words:
            return -1.0
        
        # Default: neutral
        return 0.0
    
    def score_keywords(
        self,
        df: DataFrame,
        text_column: str = "text",
        sentiment_column: Optional[str] = None
    ) -> DataFrame:
        """
        Score keywords in text based on sentiment
        
        Args:
            df: Input DataFrame
            text_column: Column containing text
            sentiment_column: Optional column with document sentiment for weighting
            
        Returns:
            DataFrame with keyword sentiment scores
        """
        # Extract keywords
        keyword_df = self.extract_keywords(df, text_column)
        
        # Calculate sentiment for each keyword
        sentiment_udf = udf(
            self.calculate_keyword_sentiment,
            DoubleType()
        )
        
        keyword_df = keyword_df.withColumn(
            "sentiment_score",
            sentiment_udf(col("keyword"))
        )
        
        # Add document sentiment if available
        if sentiment_column and sentiment_column in df.columns:
            keyword_df = keyword_df.withColumn(
                "doc_sentiment",
                col(sentiment_column)
            )
            
            # Convert doc sentiment to numeric
            keyword_df = keyword_df.withColumn(
                "doc_sentiment_num",
                when(col("doc_sentiment") == "positive", 1.0)
                .when(col("doc_sentiment") == "negative", -1.0)
                .otherwise(0.0)
            )
        
        return keyword_df
    
    def analyze_keyword_frequency(
        self,
        df: DataFrame,
        text_column: str = "text",
        top_n: int = 20
    ) -> DataFrame:
        """
        Analyze keyword frequency across all documents
        
        Args:
            df: Input DataFrame
            text_column: Column containing text
            top_n: Number of top keywords to return
            
        Returns:
            DataFrame with keyword frequencies
        """
        keyword_df = self.extract_keywords(df, text_column)
        
        freq_df = keyword_df.groupBy("keyword") \
            .agg(count(lit(1)).alias("frequency")) \
            .orderBy(col("frequency").desc())
        
        return freq_df.limit(top_n)
    
    def analyze_keyword_sentiment_trends(
        self,
        df: DataFrame,
        text_column: str = "text",
        sentiment_column: Optional[str] = None,
        group_column: Optional[str] = None
    ) -> DataFrame:
        """
        Analyze sentiment trends for keywords
        
        Args:
            df: Input DataFrame
            text_column: Column containing text
            sentiment_column: Column with document sentiment
            group_column: Optional column to group by (e.g., date, category)
            
        Returns:
            DataFrame with sentiment trends
        """
        keyword_df = self.score_keywords(df, text_column, sentiment_column)
        
        if group_column:
            # Group by specified column
            trends_df = keyword_df.groupBy(group_column, "keyword") \
                .agg(
                    spark_avg("sentiment_score").alias("avg_sentiment"),
                    count(lit(1)).alias("count")
                ) \
                .orderBy(col(group_column), col("avg_sentiment").desc())
        else:
            # Overall trends
            trends_df = keyword_df.groupBy("keyword") \
                .agg(
                    spark_avg("sentiment_score").alias("avg_sentiment"),
                    count(lit(1)).alias("count")
                ) \
                .orderBy(col("avg_sentiment").desc())
        
        return trends_df
    
    def get_sentiment_by_keyword(
        self,
        df: DataFrame,
        text_column: str = "text",
        sentiment_column: str = "sentiment"
    ) -> DataFrame:
        """
        Get sentiment distribution by keyword
        
        Args:
            df: Input DataFrame
            text_column: Column containing text
            sentiment_column: Column with document sentiment
            
        Returns:
            DataFrame with keyword sentiment distribution
        """
        keyword_df = self.score_keywords(df, text_column, sentiment_column)
        
        result_df = keyword_df.groupBy("keyword", "sentiment_score") \
            .agg(count(lit(1)).alias("count")) \
            .orderBy(col("keyword"), col("count").desc())
        
        return result_df
    
    def extract_top_keywords_by_sentiment(
        self,
        df: DataFrame,
        text_column: str = "text",
        sentiment_column: str = "sentiment",
        top_n: int = 10
    ) -> Dict[str, List[Tuple[str, int]]]:
        """
        Extract top keywords for positive and negative sentiments
        
        Args:
            df: Input DataFrame
            text_column: Column containing text
            sentiment_column: Column with document sentiment
            top_n: Number of top keywords per sentiment
            
        Returns:
            Dictionary with positive and negative top keywords
        """
        keyword_df = self.score_keywords(df, text_column, sentiment_column)
        
        # Filter by sentiment
        positive_df = keyword_df.filter(col("doc_sentiment_num") > 0)
        negative_df = keyword_df.filter(col("doc_sentiment_num") < 0)
        
        # Get top keywords
        positive_keywords = positive_df.groupBy("keyword") \
            .agg(count(lit(1)).alias("count")) \
            .orderBy(col("count").desc()) \
            .limit(top_n) \
            .collect()
        
        negative_keywords = negative_df.groupBy("keyword") \
            .agg(count(lit(1)).alias("count")) \
            .orderBy(col("count").desc()) \
            .limit(top_n) \
            .collect()
        
        return {
            "positive": [(row.keyword, int(row.count)) for row in positive_keywords],
            "negative": [(row.keyword, int(row.count)) for row in negative_keywords]
        }
    
    def calculate_document_keyword_scores(
        self,
        text: str
    ) -> Dict[str, Any]:
        """
        Calculate keyword-level sentiment scores for a single document
        
        Args:
            text: Input text
            
        Returns:
            Dictionary with keyword scores and overall sentiment
        """
        # Clean and tokenize
        clean_text = re.sub(r'[^a-z\s]', ' ', text.lower())
        tokens = word_tokenize(clean_text)
        filtered_tokens = [
            self.lemmatizer.lemmatize(token) 
            for token in tokens 
            if token not in self.stop_words and len(token) > 2
        ]
        
        # Calculate scores for each keyword
        keyword_scores = []
        total_score = 0.0
        total_keywords = 0
        
        for token in filtered_tokens:
            score = self.calculate_keyword_sentiment(token)
            if score != 0:  # Only include non-neutral keywords
                keyword_scores.append({
                    "keyword": token,
                    "score": score,
                    "sentiment": "positive" if score > 0 else "negative"
                })
                total_score += score
                total_keywords += 1
        
        # Calculate overall sentiment
        if total_keywords > 0:
            avg_score = total_score / total_keywords
            overall_sentiment = "positive" if avg_score > 0 else "negative"
            confidence = abs(avg_score)
        else:
            avg_score = 0.0
            overall_sentiment = "neutral"
            confidence = 0.0
        
        return {
            "text": text,
            "overall_sentiment": overall_sentiment,
            "overall_score": float(avg_score),
            "confidence": float(confidence),
            "keywords": keyword_scores,
            "positive_keywords": [k for k in keyword_scores if k["sentiment"] == "positive"],
            "negative_keywords": [k for k in keyword_scores if k["sentiment"] == "negative"],
            "total_keywords": total_keywords
        }
    
    def find_sentiment_drivers(
        self,
        df: DataFrame,
        text_column: str = "text",
        sentiment_column: str = "sentiment",
        min_frequency: int = 3
    ) -> DataFrame:
        """
        Find keywords that are strong drivers of sentiment
        
        Args:
            df: Input DataFrame
            text_column: Column containing text
            sentiment_column: Column with document sentiment
            min_frequency: Minimum frequency for a keyword to be considered
            
        Returns:
            DataFrame with sentiment driver keywords
        """
        keyword_df = self.score_keywords(df, text_column, sentiment_column)
        
        # Calculate sentiment correlation
        # For each keyword, calculate how often it appears in positive vs negative docs
        keyword_sentiment = keyword_df.groupBy("keyword", "doc_sentiment") \
            .agg(count(lit(1)).alias("count"))
        
        # Pivot to get counts by sentiment
        pivot_df = keyword_sentiment.groupBy("keyword") \
            .pivot("doc_sentiment") \
            .agg(spark_sum("count"))
        
        # Calculate sentiment ratio
        pivot_df = pivot_df.withColumn(
            "sentiment_ratio",
            when(col("1.0").isNull(), 0) / when(col("-1.0").isNull(), 0)
        )
        
        # Filter by frequency
        freq_df = keyword_df.groupBy("keyword") \
            .agg(count(lit(1)).alias("total_count"))
        
        result_df = pivot_df.join(freq_df, "keyword") \
            .filter(col("total_count") >= min_frequency) \
            .orderBy(col("sentiment_ratio").desc())
        
        return result_df


class KeywordSentimentTrainer:
    """
    Trains models specifically for keyword-based sentiment analysis
    """
    
    def __init__(self):
        """Initialize keyword sentiment trainer"""
        self.spark = SparkSession.builder \
            .appName("KeywordSentimentTrainer") \
            .getOrCreate()
        
        self.analyzer = KeywordSentimentAnalyzer(self.spark)
        self.keyword_model = None
        
    def train_from_dataset(
        self,
        df: DataFrame,
        text_column: str = "text",
        sentiment_column: str = "sentiment"
    ) -> Dict[str, Any]:
        """
        Train keyword sentiment model from dataset
        
        Args:
            df: Input DataFrame with text and sentiment
            text_column: Column containing text
            sentiment_column: Column with sentiment labels
            
        Returns:
            Training results
        """
        # Extract keywords and their sentiment context
        keyword_df = self.analyzer.score_keywords(df, text_column, sentiment_column)
        
        # Calculate keyword sentiment scores based on document context
        keyword_scores = keyword_df.groupBy("keyword") \
            .agg(
                spark_avg("sentiment_score").alias("avg_score"),
                spark_avg("doc_sentiment_num").alias("avg_doc_sentiment"),
                count(lit(1)).alias("frequency")
            ) \
            .filter(col("frequency") >= 2) \
            .collect()
        
        # Build keyword lexicon
        keyword_lexicon = {}
        for row in keyword_scores:
            keyword = row.keyword
            score = float(row.avg_doc_sentiment)
            
            # Only include keywords with strong sentiment
            if abs(score) > 0.3:
                keyword_lexicon[keyword] = score
        
        # Update analyzer with learned keywords
        self.analyzer.add_custom_keywords(keyword_lexicon)
        
        return {
            "keywords_learned": len(keyword_lexicon),
            "top_positive": sorted(
                [(k, v) for k, v in keyword_lexicon.items() if v > 0],
                key=lambda x: x[1],
                reverse=True
            )[:20],
            "top_negative": sorted(
                [(k, v) for k, v in keyword_lexicon.items() if v < 0],
                key=lambda x: x[1]
            )[:20]
        }
    
    def save_model(self, path: str) -> bool:
        """Save keyword model to file"""
        try:
            model_data = {
                "keyword_weights": self.analyzer.keyword_weights,
                "positive_words": list(self.analyzer.positive_words),
                "negative_words": list(self.analyzer.negative_words)
            }
            
            import json
            with open(path, 'w') as f:
                json.dump(model_data, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error saving keyword model: {e}")
            return False
    
    def load_model(self, path: str) -> bool:
        """Load keyword model from file"""
        try:
            import json
            with open(path, 'r') as f:
                model_data = json.load(f)
            
            self.analyzer.keyword_weights = model_data.get("keyword_weights", {})
            self.analyzer.positive_words = set(model_data.get("positive_words", []))
            self.analyzer.negative_words = set(model_data.get("negative_words", []))
            
            return True
        except Exception as e:
            logger.error(f"Error loading keyword model: {e}")
            return False


# Example usage
if __name__ == "__main__":
    from pyspark.sql import SparkSession
    from pathlib import Path
    
    spark = SparkSession.builder \
        .appName("KeywordAnalysisTest") \
        .getOrCreate()
    
    # Load dataset
    data_path = "/workspace/github__rskworld__sentiment-analysis/data/sentiment_data.csv"
    df = spark.read.csv(
        data_path,
        header=True,
        inferSchema=True,
        comment="#"
    )
    
    # Initialize analyzer
    analyzer = KeywordSentimentAnalyzer(spark)
    
    # Analyze keyword frequency
    print("\n=== Top Keywords ===")
    freq_df = analyzer.analyze_keyword_frequency(df, "text")
    freq_df.show()
    
    # Analyze a single document
    print("\n=== Single Document Analysis ===")
    text = "This product is absolutely amazing and excellent quality!"
    result = analyzer.calculate_document_keyword_scores(text)
    print(json.dumps(result, indent=2))
    
    # Find sentiment drivers
    print("\n=== Sentiment Drivers ===")
    drivers_df = analyzer.find_sentiment_drivers(df, "text", "sentiment")
    drivers_df.show()
    
    spark.stop()
