-- migrate:up

-- Table: candidates
CREATE TABLE candidates (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_name VARCHAR(255),
    cv_file_path VARCHAR(500) NOT NULL,
    report_file_path VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: jobs
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    description TEXT,
    requirements TEXT, -- rubric detail
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: queues
CREATE TABLE queues (
    id INT AUTO_INCREMENT PRIMARY KEY,
    upload_id INT NOT NULL,
    source ENUM('jobs','candidates') NOT NULL,
    status ENUM('queued','processing','completed','failed') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table: results
CREATE TABLE results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    queue_id INT NOT NULL UNIQUE,
    cv_match_rate FLOAT,
    cv_feedback TEXT,
    project_score FLOAT,
    project_feedback TEXT,
    overall_summary TEXT,
    raw_output JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_results_queue FOREIGN KEY (queue_id) REFERENCES queues(id) ON DELETE CASCADE
);

-- Indexes for faster queries
CREATE INDEX idx_queue_status ON queues(status);
CREATE INDEX idx_queue_source ON queues(source);
CREATE INDEX idx_upload_source ON queues(upload_id, source);
CREATE INDEX idx_results_queue_id ON results(queue_id);

-- migrate:down
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS queues;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS candidates;
