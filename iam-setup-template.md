Policy ARN: arn:aws:iam::131471595295:policy/HybridS3UploaderPolicy
Policy ARN: arn:aws:iam::131471595295:policy/leastprivilages3+delObj-policy
Group ARN: arn:aws:iam::131471595295:policy/HybridS3UploaderPolicy
group leastprivilage and user fortest created, policy attached to group



"UserName": "fortest",
"UserId": "AIDAR5HCRK4P2B5GRSD33",
"Arn": "arn:aws:iam::131471595295:user/fortest"
"GroupName": "leastprivilage",
"GroupId": "AGPAR5HCRK4PRS3GUWTEC",
"Arn": "arn:aws:iam::131471595295:group/leastprivilage"



Created access key and CLI profile for fortest user



Created role for lambda, assumed it and attached a policy to it 
Role's ARN: arn:aws:iam::131471595295:role/lambda-s3-LPP-role



CloudFormation for repeatability:

S3 bucket

IAM policy

IAM role



ARN: arn:aws:iam::131471595295:role/lambda-s3-LPP-role

