-- migrate:up

-- Table: uploads
CREATE TABLE uploads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    candidate_name VARCHAR(255),
    cv_file_path VARCHAR(500) NOT NULL,
    report_file_path VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: jobs
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    upload_id INT NOT NULL,
    status ENUM('queued','processing','completed','failed') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_jobs_upload FOREIGN KEY (upload_id) REFERENCES uploads(id) ON DELETE CASCADE
);

-- Table: results
CREATE TABLE results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL UNIQUE,
    cv_match_rate FLOAT,
    cv_feedback TEXT,
    project_score FLOAT,
    project_feedback TEXT,
    overall_summary TEXT,
    raw_output JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_results_job FOREIGN KEY (job_id) REFERENCES jobs(id) ON DELETE CASCADE
);

-- Indexes for faster queries
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_results_job_id ON results(job_id);

-- migrate:down
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS jobs;
DROP TABLE IF EXISTS uploads;
