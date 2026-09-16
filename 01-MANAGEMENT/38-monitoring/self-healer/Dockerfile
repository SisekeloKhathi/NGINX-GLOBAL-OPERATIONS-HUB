# I am basing on python:3.12-alpine because it is small (about 50MB)
# and matches the runtime the display-api uses. Using the same base
# keeps the images predictable. Reference: Docker Hub python image
# page, alpine variants.
FROM python:3.12-alpine

# I am setting the working directory inside the container. All
# subsequent COPY and RUN commands are relative to this path.
WORKDIR /app

# I am copying requirements first, then running pip install, then
# copying the source. This ordering lets Docker cache the pip layer
# across rebuilds — if only self_healer.py changes, the pip install
# step is reused from cache. Reference: Dockerfile best practices,
# "leverage build cache" section.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# I am copying the actual application code after the dependencies
# so source changes do not invalidate the dependency layer.
COPY self_healer.py .

# I am declaring the port the Flask app listens on. EXPOSE is
# documentation — the actual port mapping happens in the container
# runtime. Reference: Dockerfile reference, EXPOSE instruction.
EXPOSE 5002

# I am starting the app with python so there is no shell in between
# and PID 1 is python itself, which lets it receive SIGTERM for
# clean shutdown. Reference: Dockerfile reference, CMD in exec form.
CMD ["python", "self_healer.py"]
