# Update JSON Script

This folder contains the Python Script that runs every minute to update the satellite information. It takes the updated satellite information, formats it into a JSON file, and uploads it to AWS S3 bucket. Our website then pulls from this JSON file stored in AWS in our visualization tool.

This scripts runs on our AWS Virual Machine
