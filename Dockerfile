# Step 1: Build stage
FROM maven:3.9.6-eclipse-temurin-21 AS build

WORKDIR /build
COPY pom.xml .
COPY src ./src
RUN mvn -B -Dmaven.test.skip=true clean package

# Step 2: Runtime stage
FROM eclipse-temurin:21-jdk-jammy

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy Spring Boot jar from build stage
COPY --from=build /build/target/*.jar app.jar

# Copy Python files
COPY ml.py .
COPY requirements.txt .

# Install Python dependencies
RUN test -f requirements.txt && pip3 install --no-cache-dir -r requirements.txt || true

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
