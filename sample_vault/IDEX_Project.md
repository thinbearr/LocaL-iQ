## AI-Based Electrical Design Documentation System for Ship Cable Routing and Material Optimization 

## TECHNOLOGY DOMAIN 

Artificial Intelligence and Machine Learning 

## DESCRIPTION 

This project proposes the development of an AI-assisted system to automate the generation of electrical design documentation for ship cable routing. The system processes ship design drawings and cable data to determine optimal routing paths, select appropriate materials and cable glands, validate engineering constraints, and generate structured documentation. 

The solution combines rule-based engineering logic with targeted artificial intelligence modules to improve efficiency, reduce manual effort, and support cost-effective material selection. The system is designed for secure on-premise deployment and supports engineer review and approval before final . implementation 

## PROBLEM STATEMENT 

- Cable routing through ship compartments is performed manually using complex ship drawings. 

- Selection of appropriate cable glands and materials requires manual reference to engineering standards. 

- Calculation of cable tray filling and validation of routing logic is timeconsuming and prone to errors. 

- Generation of electrical design documentation and Bills of Materials (BOM) requires significant manual effort. 

- Ensuring compliance with engineering standards is difficult and requires repeated manual checks. 

## APPROACH 

- A rule-based engineering approach is used to ensure compliant cable routing and material selection. 

- Cost optimization is considered in routing and material decisions. 

- Artificial intelligence is used to support analysis and detect anomalies. 

- Engineers review and approve all system-generated decisions. 

- The system is designed for secure on-premise deployment. 

## SYSTEM WORKFLOW / METHODOLOGY 

STEP 1 — INPUT DATA ACQUISITION AND PREPARATION 

- The user provides the ship design drawing in DXF, DWG, or PDF format. 

- The system extracts structural information such as compartments, boundaries, cable trays, and labels. 

- Cable connection data is provided through a cable schedule in Excel, CSV, or PDF format. 

- If a cable schedule is not available, manual entry of cable connections is supported. 

- All input data is validated before further processing. 

STEP 2 — SPATIAL MODEL GENERATION AND LAYOUT STRUCTURING 

- Extracted geometric and textual data is converted into structured layout elements. 

- Compartments are identified from closed boundaries. 

- Cable trays and pathway segments are identified from line and polyline elements. 

- Structural boundaries are recognized to define routing constraints. 

- Zone classifications are assigned based on engineering rules. 

- A connectivity graph representing possible cable paths is generated. 

- The spatial model is stored for routing and analysis. 

## STEP 3 — CABLE ROUTING PATH CALCULATION 

- Source and destination points are determined for each cable. 

- Possible routing paths are identified using the connectivity graph. 

- Routing algorithms compute feasible cable routes considering constraints and permissible zones. 

- Invalid routes violating structural or capacity limits are automatically excluded. 

- One or more compliant routing options are generated. 

- Routing results are stored for material selection and validation. 

## STEP 4 — MATERIAL AND CABLE GLAND SELECTION 

- The system analyses routing paths to identify penetration points and compartments. 

- Appropriate cable gland types are selected based on cable characteristics and standards. 

- Materials are selected from the catalogue based on compatibility and compliance requirements. 

- Multiple compliant material options may be evaluated for cost efficiency. 

- Selected materials and specifications are recorded. 

- Material data is prepared for validation and reporting. 

## STEP 5 — VALIDATION AND CAPACITY VERIFICATION 

- Cable routes are evaluated for compliance with routing rules and zone restrictions. 

- Cable tray utilization is calculated to verify capacity limits. 

- Material and gland selections are checked against engineering standards. 

- Non-compliant routes or selections are flagged for correction. 

- Validation results are recorded for documentation. 

## STEP 6 — DOCUMENTATION AND REPORT GENERATION 

- Validated routing and material data is compiled into structured engineering outputs. 

- Cable routing diagrams are generated. 

- A Bill of Materials (BOM) is automatically created. 

- Cable tray capacity and utilization reports are generated. 

- Documentation is formatted for engineering review and approval. 

- Outputs are stored for project records. 

STEP 7 — HUMAN REVIEW AND APPROVAL 

- Routing diagrams and reports are presented to the engineer. 

- The engineer reviews routing and material selections. 

- Validation warnings and anomalies are highlighted. 

- The engineer may approve or request modifications. 

- Approved documentation is finalized for implementation. 

- All actions are recorded for traceability. 

STEP 8 — SECURE STORAGE AND AUDIT LOGGING 

- Final routing and documentation data is stored securely in the database. 

- User actions and system decisions are recorded in the audit log. 

- Version history of design changes is maintained. 

- Access to data is controlled through authentication and authorization. 

- Project records are archived for future reference and compliance review. 

## TECHNOLOGY STACK 

STEP 1 — INPUT DATA PROCESSING Read DXF drawings → ezdxf Parse vector PDFs → PyMuPDF / pdfplumber Convert scanned PDFs to images → pdf2image Preprocess images → OpenCV Extract text from drawings → Tesseract OCR Read cable schedule → pandas / openpyxl Detect objects in scanned drawings (optional) → YOLOv8 

STEP 2 — SPATIAL MODEL GENERATION Process geometry → Shapely Perform numerical calculations → NumPy Build connectivity graph → NetworkX Store layout data → PostgreSQL / SQLite Interpret labels (optional) → Sentence Transformer 

STEP 3 — ROUTING 

Find shortest path → Dijkstra algorithm Optimize routing for large layouts → A* algorithm Compute routing cost → Python weighted cost logic Visualize routes → Matplotlib / Plotly 

STEP 4 — MATERIAL SELECTION Store material catalogue → PostgreSQL Apply engineering rules → Python rule engine Recommend cost-effective materials → Decision Tree / Random Forest 

STEP 5 — VALIDATION Validate routing rules → Python rule engine Calculate tray capacity → NumPy Detect anomalies → Isolaton Forest 

STEP 6 — DOCUMENTATION Generate reports → Python Export PDF reports → ReportLab Export Excel reports → pandas / openpyxl 

STEP 7 — USER INTERFACE Frontend interface → React / Vite Backend API → FastAPI User authentication → JWT Decision explanation → Local LLM via Ollama 

STEP 8 — DEPLOYMENT AND SECURITY Database → PostgreSQL Logging → Python logging module Access control → JWT authentcaton Deployment → Docker 

## DEPLOYMENT 

The system is deployed on-premise using Docker containers to ensure data security and offline operation. All components including frontend, backend, processing modules, and database run locally within the organization’s network environment. 

The system is designed to operate efficiently on standard hardware and can scale by adding computational resources when required. 

## EXPECTED OUTPUTS 

- Cable Routing Diagram 

- Cable Gland Specification List 

- Cable Tray Utilization Report 

- Bill of Materials (BOM) 

- Engineering Documentation 

- Audit Log Records 

## SYSTEM OBJECTIVE 

Automate cable routing and material selection processes to reduce manual effort, improve accuracy, ensure compliance with engineering standards, and support cost optimization in ship electrical design documentation. 

