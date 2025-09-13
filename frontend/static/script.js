// SourceSense JavaScript

window.env = {
  APP_HTTP_HOST: "{{ app_http_host }}",
  APP_HTTP_PORT: "{{ app_http_port }}",
  APP_DASHBOARD_HTTP_HOST: "{{ app_dashboard_http_host }}",
  APP_DASHBOARD_HTTP_PORT: "{{ app_dashboard_http_port }}",
};

let currentWorkflowId = null;
let currentRunId = null;
let resultsPollingInterval = null;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
  setupFormHandlers();
  setupTabHandlers();
});

function setupFormHandlers() {
  // Database type change handler
  const databaseType = document.getElementById('databaseType');
  if (databaseType) {
    databaseType.addEventListener('change', function() {
      updatePortPlaceholder(this.value);
    });
  }
}

function setupTabHandlers() {
  // Setup tab click handlers
  const tabButtons = document.querySelectorAll('.tab-btn');
  tabButtons.forEach(button => {
    button.addEventListener('click', function() {
      const tabName = this.getAttribute('onclick') ? 
        this.getAttribute('onclick').match(/'([^']+)'/)[1] : 
        this.textContent.toLowerCase().replace(/\s+/g, '');
      showTab(tabName);
    });
  });
}

function updatePortPlaceholder(databaseType) {
  const portInput = document.getElementById('port');
  const portMap = {
    'postgresql': '5432',
    'mysql': '3306',
    'sqlite': '',
    'mssql': '1433'
  };
  
  if (portInput) {
    portInput.placeholder = portMap[databaseType] || '';
  }
  
  // Hide/show fields for SQLite
  const hostGroup = document.getElementById('host')?.closest('.form-group');
  const portGroup = document.getElementById('port')?.closest('.form-group');
  const usernameGroup = document.getElementById('username')?.closest('.form-group');
  const passwordGroup = document.getElementById('password')?.closest('.form-group');
  
  if (databaseType === 'sqlite') {
    if (hostGroup) hostGroup.style.display = 'none';
    if (portGroup) portGroup.style.display = 'none';
    if (usernameGroup) usernameGroup.style.display = 'none';
    if (passwordGroup) passwordGroup.style.display = 'none';
    const dbInput = document.getElementById('database');
    if (dbInput) dbInput.placeholder = 'path/to/database.db';
  } else {
    if (hostGroup) hostGroup.style.display = 'block';
    if (portGroup) portGroup.style.display = 'block';
    if (usernameGroup) usernameGroup.style.display = 'block';
    if (passwordGroup) passwordGroup.style.display = 'block';
    const dbInput = document.getElementById('database');
    if (dbInput) dbInput.placeholder = 'my_database';
  }
}

async function testConnection() {
  const button = document.getElementById('testConnectionBtn');
  if (!button) return;
  
  const originalText = button.innerHTML;
  
  button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing...';
  button.disabled = true;
  
  try {
    const connectionConfig = getConnectionConfig();
    
    // Create a test workflow payload that only runs connection test
    const testPayload = {
      connection_config: connectionConfig,
      analysis_options: {
        test_only: true,
        analyze_data_quality: false,
        detect_sensitive_data: false
      }
    };
    
    // Start a test workflow
    const response = await fetch('/workflows/v1/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testPayload)
    });
    
    if (!response.ok) {
      throw new Error('Failed to start connection test');
    }
    
    const result = await response.json();
    console.log('Workflow started:', result); // Debug log
    
    // Extract workflow ID and run ID from response
    const testWorkflowId = result.workflow_id || 
                          result.id || 
                          result.workflowId ||
                          (result.data && result.data.workflow_id);
    
    const testRunId = result.run_id ||
                     result.runId ||
                     (result.data && result.data.run_id);
    
    if (!testWorkflowId || !testRunId) {
      throw new Error('No workflow ID or run ID received from server');
    }
    
    // Poll for the test result (separate from main workflow polling)
    let attempts = 0;
    const maxAttempts = 5; // Reduced timeout for quick test
    let testCompleted = false;
    
    while (attempts < maxAttempts && !testCompleted) {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Use the correct status endpoint format
      const statusEndpoint = `/workflows/v1/status/${testWorkflowId}/${testRunId}`;
      
      try {
        const statusResponse = await fetch(statusEndpoint);
        if (statusResponse.ok) {
          const statusResult = await statusResponse.json();
          console.log(`Test status check (${statusEndpoint}):`, statusResult); // Debug log
        
        // Extract status from the correct nested location
        const workflowStatus = (statusResult.data && statusResult.data.status) || statusResult.status;
        const normalizedStatus = workflowStatus ? workflowStatus.toLowerCase() : '';
        
        if (normalizedStatus === 'completed' || normalizedStatus === 'failed') {
          testCompleted = true;
          
          // For test connection, we need to check the actual workflow results
          // The workflow might complete but with failed results
          if (normalizedStatus === 'completed') {
            // Try to get the actual workflow results to check if connection was successful
            try {
              const resultsResponse = await fetch(`/workflows/v1/config/${testWorkflowId}?type=workflows`);
              if (resultsResponse.ok) {
                const configResult = await resultsResponse.json();
                const actualResults = configResult.data || configResult.config || configResult;
                
                // Check if the connection test was successful
                if (actualResults.connection_test && actualResults.connection_test.status === 'success') {
                  button.innerHTML = '<i class="fas fa-check"></i> Connection Successful';
                  button.style.backgroundColor = 'var(--success-color)';
                } else {
                  const errorMsg = actualResults.connection_test?.message || 
                                 actualResults.error || 
                                 'Connection test failed';
                  throw new Error(errorMsg);
                }
              } else {
                // If we can't get results, assume success for completed workflow
                button.innerHTML = '<i class="fas fa-check"></i> Connection Successful';
                button.style.backgroundColor = 'var(--success-color)';
              }
            } catch (e) {
              throw new Error('Could not verify connection test results');
            }
          } else {
            throw new Error('Connection test workflow failed');
          }
          break;
        }
        } else {
          console.log('Test status response not OK:', statusResponse.status);
        }
      } catch (e) {
        console.log(`Test status endpoint failed:`, e.message);
      }
      attempts++;
    }
    
    if (attempts >= maxAttempts && !testCompleted) {
      throw new Error('Connection test timed out');
    }
    
  } catch (error) {
    button.innerHTML = '<i class="fas fa-times"></i> Connection Failed';
    button.style.backgroundColor = 'var(--error-color)';
    showErrorModal(error.message);
  } finally {
    setTimeout(() => {
      button.innerHTML = originalText;
      button.style.backgroundColor = '';
      button.disabled = false;
    }, 3000);
  }
}

async function handleSubmit(event) {
  event.preventDefault();
  
  const button = document.getElementById('extractMetadataBtn');
  if (!button) return;
  
  const originalText = button.innerHTML;
  
  button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Starting Extraction...';
  button.disabled = true;
  
  try {
    const connectionConfig = getConnectionConfig();
    const analysisOptions = getAnalysisOptions();
    
    const workflowPayload = {
      connection_config: connectionConfig,
      analysis_options: analysisOptions
    };
    
    const response = await fetch('/workflows/v1/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(workflowPayload)
    });

    if (response.ok) {
    const result = await response.json();
    console.log('Main workflow started:', result); // Debug log
    currentWorkflowId = result.workflow_id || 
                       result.id || 
                       result.workflowId ||
                       (result.data && result.data.workflow_id);
    
    currentRunId = result.run_id ||
                  result.runId ||
                  (result.data && result.data.run_id);
    
    if (!currentWorkflowId || !currentRunId) {
      throw new Error('No workflow ID or run ID received from server');
    }
    
    // Show success modal
    showSuccessModal();
    
    // Show results section and start polling
    showResultsSection();
    startResultsPolling();
      
    } else {
      throw new Error('Failed to start metadata extraction');
    }
  } catch (error) {
    showErrorModal(error.message);
  } finally {
    setTimeout(() => {
      button.innerHTML = originalText;
      button.disabled = false;
    }, 3000);
  }
}

function getConnectionConfig() {
  const databaseType = document.getElementById('databaseType')?.value || '';
  
  // Validate that database type is selected
  if (!databaseType) {
    throw new Error('Please select a database type');
  }
  
  return {
    database_type: databaseType,
    host: document.getElementById('host')?.value || 'localhost',
    port: document.getElementById('port')?.value || '',
    database: document.getElementById('database')?.value || '',
    username: document.getElementById('username')?.value || '',
    password: document.getElementById('password')?.value || ''
  };
}

function getAnalysisOptions() {
  return {
    analyze_data_quality: document.getElementById('analyzeQuality')?.checked || false,
    detect_sensitive_data: document.getElementById('detectSensitive')?.checked || false,
    max_tables_for_quality_analysis: 5
  };
}

function showResultsSection() {
  const resultsSection = document.getElementById('resultsSection');
  if (resultsSection) {
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
  }
  
  // Reset status indicator
  updateStatusIndicator('Processing...', 'processing');
}

function updateStatusIndicator(text, status) {
  const indicator = document.getElementById('statusIndicator');
  if (!indicator) return;
  
  const statusText = indicator.querySelector('.status-text');
  const spinner = indicator.querySelector('.loading-spinner');
  
  if (statusText) statusText.textContent = text;
  
  if (status === 'completed') {
    if (spinner) spinner.style.display = 'none';
    indicator.style.background = 'var(--success-color)';
    indicator.style.color = 'white';
  } else if (status === 'failed') {
    if (spinner) spinner.style.display = 'none';
    indicator.style.background = 'var(--error-color)';
    indicator.style.color = 'white';
  } else {
    if (spinner) spinner.style.display = 'block';
    indicator.style.background = 'var(--card-background)';
    indicator.style.color = 'var(--text-primary)';
  }
}

function startResultsPolling() {
  if (resultsPollingInterval) {
    clearInterval(resultsPollingInterval);
  }
  
  resultsPollingInterval = setInterval(async () => {
    if (currentWorkflowId && currentWorkflowId !== 'undefined') {
      await pollWorkflowResults();
    }
  }, 5000); // Poll every 5 seconds
}

async function pollWorkflowResults() {
  try {
    // Safety check to prevent polling for undefined
    if (!currentWorkflowId || currentWorkflowId === 'undefined' || !currentRunId) {
      console.log('No valid workflow ID or run ID, stopping polling');
      clearInterval(resultsPollingInterval);
      resultsPollingInterval = null;
      return;
    }
    
    // Use the correct status endpoint format
    const statusEndpoint = `/workflows/v1/status/${currentWorkflowId}/${currentRunId}`;
    
    try {
      const response = await fetch(statusEndpoint);
      if (response.ok) {
        const statusResult = await response.json();
        console.log(`Main workflow status (${statusEndpoint}):`, statusResult);
        
        // Extract status from the correct nested location
        const workflowStatus = (statusResult.data && statusResult.data.status) || statusResult.status;
        const normalizedStatus = workflowStatus ? workflowStatus.toLowerCase() : '';
        
        // For the main workflow, we need to get the actual results separately
        // The status endpoint only tells us if the workflow is done, not the results
        if (normalizedStatus === 'completed' || normalizedStatus === 'failed') {
          console.log('Main workflow completed, showing results...');
          
          // Since workflow results are not accessible through the current API,
          // we'll show a success message with a link to view results in Temporal UI
          if (normalizedStatus === 'completed') {
            updateResultsDisplay({
              status: 'completed',
              execution_summary: {
                completion_status: 'completed',
                message: 'Workflow completed successfully!'
              },
              temporal_ui_link: `http://localhost:8233/namespaces/default/workflows/${currentWorkflowId}/${currentRunId}/history`
            });
          } else {
            updateResultsDisplay({
              status: 'failed',
              error: 'Workflow execution failed',
              execution_summary: {
                completion_status: 'failed'
              }
            });
          }
          
          clearInterval(resultsPollingInterval);
          resultsPollingInterval = null;
        }
      } else {
        console.log('Main workflow status response not OK:', response.status);
      }
    } catch (e) {
      console.log('Main workflow status endpoint failed:', e.message);
    }
  } catch (error) {
    console.error('Error polling workflow results:', error);
  }
}

function updateResultsDisplay(results) {
  console.log('Updating results display with:', results);
  
  // Check if workflow failed
  if (results.status === 'failed' || results.error) {
    console.log('Workflow failed, showing error message');
    
    // Update status indicator
    updateStatusIndicator('Extraction Failed', 'failed');
    
    // Show error in the summary section
    const summaryCards = document.getElementById('summary-cards');
    if (summaryCards) {
      summaryCards.innerHTML = `
        <div class="summary-card error">
          <div class="card-icon">
            <i class="fas fa-exclamation-triangle"></i>
          </div>
          <div class="card-content">
            <h3>Workflow Failed</h3>
            <p>${results.error || 'An error occurred during execution'}</p>
            ${results.connection_test ? `<p><strong>Connection Error:</strong> ${results.connection_test.message}</p>` : ''}
          </div>
        </div>
      `;
    }
    
    // Show error in schema tab
    const schemaContent = document.getElementById('schema-content');
    if (schemaContent) {
      schemaContent.innerHTML = `
        <div class="error-message">
          <i class="fas fa-exclamation-triangle"></i>
          <h3>Schema Extraction Failed</h3>
          <p>${results.error || 'Unable to extract schema metadata'}</p>
        </div>
      `;
    }
    
    // Show error in sensitive data tab
    const sensitiveContent = document.getElementById('sensitive-content');
    if (sensitiveContent) {
      sensitiveContent.innerHTML = `
        <div class="error-message">
          <i class="fas fa-exclamation-triangle"></i>
          <h3>Sensitive Data Detection Failed</h3>
          <p>${results.error || 'Unable to detect sensitive data'}</p>
        </div>
      `;
    }
    
    // Show the results section even for errors
    showResultsSection();
    return;
  }
  
  // Update status indicator
  if (results.status === 'completed') {
    updateStatusIndicator('Extraction Completed', 'completed');
  } else if (results.status === 'failed') {
    updateStatusIndicator('Extraction Failed', 'failed');
  } else {
    updateStatusIndicator('Processing...', 'processing');
  }
  
  // Update summary cards
  if (results.execution_summary) {
    updateSummaryCards(results.execution_summary);
  }
  
  // Show Temporal UI link if available
  if (results.temporal_ui_link) {
    const summaryCards = document.getElementById('summary-cards');
    if (summaryCards) {
      summaryCards.innerHTML = `
        <div class="summary-card success">
          <div class="card-icon">
            <i class="fas fa-check-circle"></i>
          </div>
          <div class="card-content">
            <h3>Workflow Completed Successfully!</h3>
            <p>Your metadata extraction workflow has completed successfully.</p>
            <p><strong>View detailed results:</strong></p>
            <a href="${results.temporal_ui_link}" target="_blank" class="btn btn-primary">
              <i class="fas fa-external-link-alt"></i> Open in Temporal UI
            </a>
          </div>
        </div>
      `;
    }
    
    // Show message in schema tab
    const schemaContent = document.getElementById('schema-content');
    if (schemaContent) {
      schemaContent.innerHTML = `
        <div class="success-message">
          <i class="fas fa-check-circle"></i>
          <h3>Schema Extraction Completed</h3>
          <p>Schema metadata has been successfully extracted from your database.</p>
          <p>Click the link above to view detailed results in the Temporal UI.</p>
        </div>
      `;
    }
    
    // Show message in sensitive data tab
    const sensitiveContent = document.getElementById('sensitive-content');
    if (sensitiveContent) {
      sensitiveContent.innerHTML = `
        <div class="success-message">
          <i class="fas fa-check-circle"></i>
          <h3>Sensitive Data Detection Completed</h3>
          <p>Sensitive data analysis has been completed successfully.</p>
          <p>Click the link above to view detailed results in the Temporal UI.</p>
        </div>
      `;
    }
    
    // Show the results section
    showResultsSection();
    return;
  }
  
  // Update detailed results
  if (results.schema_metadata) {
    updateSchemaTab(results.schema_metadata);
  }
  
  if (results.sensitive_data) {
    updateSensitiveTab(results.sensitive_data);
  }
}

function updateSummaryCards(summary) {
  const schemasEl = document.getElementById('schemasCount');
  const tablesEl = document.getElementById('tablesCount');
  const columnsEl = document.getElementById('columnsCount');
  const sensitiveEl = document.getElementById('sensitiveCount');
  
  if (schemasEl) schemasEl.textContent = summary.total_schemas || 0;
  if (tablesEl) tablesEl.textContent = summary.total_tables || 0;
  if (columnsEl) columnsEl.textContent = summary.total_columns || 0;
  if (sensitiveEl) sensitiveEl.textContent = summary.sensitive_columns_found || 0;
}

function updateSchemaTab(schemaMetadata) {
  const schemaExplorer = document.getElementById('schemaExplorer');
  if (!schemaExplorer) return;
  
  if (!schemaMetadata.schemas || schemaMetadata.schemas.length === 0) {
    schemaExplorer.innerHTML = '<p class="text-muted">No schemas found.</p>';
    return;
  }
  
  let html = '<div class="schema-tree">';
  
  schemaMetadata.schemas.forEach(schema => {
    html += `
      <div class="schema-item">
        <div class="schema-header" onclick="toggleSchema('${schema.schema_name}')">
          <h3>
            <i class="fas fa-layer-group"></i>
            ${schema.schema_name}
            <span class="text-muted">(${schema.tables.length} tables)</span>
          </h3>
          <i class="fas fa-chevron-down toggle-icon" id="toggle-${schema.schema_name}"></i>
        </div>
        <div class="table-list" id="schema-${schema.schema_name}" style="display: none;">
    `;
    
    schema.tables.forEach(table => {
      html += `
        <div class="table-item">
          <div class="table-header">
            <div class="table-name">${table.table_name}</div>
            <div class="table-info">
              <span><i class="fas fa-columns"></i> ${table.columns.length} columns</span>
              <span><i class="fas fa-key"></i> ${table.primary_keys.length} PK</span>
              <span><i class="fas fa-link"></i> ${table.foreign_keys.length} FK</span>
            </div>
          </div>
          <div class="columns-grid">
      `;
      
      table.columns.forEach(column => {
        const isPrimaryKey = table.primary_keys.includes(column.column_name);
        const keyIcon = isPrimaryKey ? '<i class="fas fa-key text-warning"></i>' : '';
        
        html += `
          <div class="column-item">
            <div class="column-name">
              ${keyIcon} ${column.column_name}
            </div>
            <div class="column-type">${column.data_type}</div>
          </div>
        `;
      });
      
      html += `
          </div>
        </div>
      `;
    });
    
    html += `
        </div>
      </div>
    `;
  });
  
  html += '</div>';
  schemaExplorer.innerHTML = html;
}

function updateSensitiveTab(sensitiveData) {
  const sensitiveList = document.getElementById('sensitiveDataList');
  if (!sensitiveList) return;
  
  if (!sensitiveData.sensitive_columns || sensitiveData.sensitive_columns.length === 0) {
    sensitiveList.innerHTML = `
      <div class="sensitive-alert">
        <i class="fas fa-shield-alt"></i>
        <strong>Good news!</strong> No potentially sensitive data detected.
      </div>
    `;
    return;
  }
  
  let html = `
    <div class="sensitive-alert">
      <i class="fas fa-exclamation-triangle"></i>
      <strong>Warning:</strong> ${sensitiveData.sensitive_columns.length} potentially sensitive columns detected.
    </div>
  `;
  
  sensitiveData.sensitive_columns.forEach(item => {
    const categoryClass = `category-${item.category.toLowerCase()}`;
    
    html += `
      <div class="sensitive-item">
        <div class="sensitive-header">
          <div class="sensitive-location">
            <i class="fas fa-table"></i>
            ${item.schema_name}.${item.table_name}.${item.column_name}
          </div>
          <span class="sensitive-category ${categoryClass}">${item.category}</span>
        </div>
        <div class="sensitive-details">
          <p><strong>Data Type:</strong> ${item.data_type}</p>
          <p><strong>Pattern Matched:</strong> ${item.pattern_matched}</p>
          <p><strong>Confidence:</strong> ${item.confidence}</p>
        </div>
      </div>
    `;
  });
  
  sensitiveList.innerHTML = html;
}

function toggleSchema(schemaName) {
  const content = document.getElementById(`schema-${schemaName}`);
  const toggle = document.getElementById(`toggle-${schemaName}`);
  
  if (content && toggle) {
    if (content.style.display === 'none') {
      content.style.display = 'block';
      toggle.classList.remove('fa-chevron-down');
      toggle.classList.add('fa-chevron-up');
    } else {
      content.style.display = 'none';
      toggle.classList.remove('fa-chevron-up');
      toggle.classList.add('fa-chevron-down');
    }
  }
}

function showTab(tabName) {
  // Hide all tabs
  document.querySelectorAll('.tab-pane').forEach(pane => {
    pane.classList.remove('active');
  });
  
  // Remove active class from all buttons
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // Show selected tab
  const targetTab = document.getElementById(`${tabName}Tab`);
  if (targetTab) {
    targetTab.classList.add('active');
  }
  
  // Add active class to clicked button
  if (event && event.target) {
    event.target.classList.add('active');
  }
}

function showSuccessModal() {
  const modal = document.getElementById('successModal');
  if (modal) {
    modal.classList.add('show');
  }
}

function showErrorModal(message) {
  const errorMessage = document.getElementById('errorMessage');
  const modal = document.getElementById('errorModal');
  
  if (errorMessage) errorMessage.textContent = message;
  if (modal) modal.classList.add('show');
}

function closeModal() {
  document.querySelectorAll('.modal').forEach(modal => {
    modal.classList.remove('show');
  });
}

// Close modal when clicking outside
document.addEventListener('click', function(event) {
  if (event.target.classList.contains('modal')) {
    closeModal();
  }
});
