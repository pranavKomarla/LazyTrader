// MongoDB initialization script
// This script runs when the MongoDB container starts for the first time

// Switch to the stockapp database
db = db.getSiblingDB('stockapp');

// Create collections
db.createCollection('news_articles');
db.createCollection('market_data');
db.createCollection('user_preferences');

// Create indexes for better performance
db.news_articles.createIndex({ "published_at": -1 });
db.news_articles.createIndex({ "title": "text", "content": "text" });
db.market_data.createIndex({ "symbol": 1, "timestamp": -1 });

// Insert some sample data
db.news_articles.insertMany([
  {
    title: "Sample Market News Article",
    content: "This is a sample news article for testing purposes.",
    published_at: new Date(),
    source: "Sample Source",
    category: "market_news"
  }
]);

print("MongoDB initialization completed successfully!");

