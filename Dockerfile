# ============================================================
#  RecoverAI – Containerized Deleted-File Recovery & ML Pipeline
#  Base: Ubuntu 22.04 LTS (slim)
# ============================================================
FROM ubuntu:22.04

LABEL maintainer="RecoverAI Research Team"
LABEL description="Predictive Deleted File Recovery with Semantic Search"
LABEL version="2.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# ── System packages ──────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Filesystem forensics tools
    e2fsprogs \
    dosfstools \
    f2fs-tools \
    ntfs-3g \
    util-linux \
    # File processing
    poppler-utils \
    libmagic1 \
    # Python & build tools
    python3.11 \
    python3-pip \
    python3.11-dev \
    build-essential \
    # Utilities
    git \
    curl \
    sudo \
    vim \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Make python3 point to python3.11
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/python  python  /usr/bin/python3.11 1

# Allow root to mount loop devices inside container
RUN echo "root ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# ── Python dependencies ───────────────────────────────────────
COPY requirements.txt /tmp/requirements.txt
RUN pip3 install --no-cache-dir --upgrade pip && \
    pip3 install --no-cache-dir -r /tmp/requirements.txt

# ── App directory ─────────────────────────────────────────────
WORKDIR /app
COPY . /app

# Pre-download SentenceTransformer model at build time (avoids cold-start)
RUN python3 -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')" || true

# Create output directories
RUN mkdir -p /app/outputs /app/db /tmp/recoverai_experiment

# ── Entry point ───────────────────────────────────────────────
EXPOSE 8888
CMD ["python3", "run_pipeline_v2.py"]
