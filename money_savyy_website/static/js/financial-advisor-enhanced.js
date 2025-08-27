class ProfessionalFinancialAdvisor {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 5;
        this.analysisData = null;
        this.charts = {};
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Tab switching events
        document.addEventListener('DOMContentLoaded', () => {
            this.setupTabNavigation();
        });
    }

    setupTabNavigation() {
        const tabLinks = document.querySelectorAll('[data-bs-toggle="pill"]');
        tabLinks.forEach(link => {
            link.addEventListener('shown.bs.tab', (event) => {
                const targetTab = event.target.getAttribute('href').substring(1);
                this.handleTabSwitch(targetTab);
            });
        });
    }

    handleTabSwitch(tabName) {
        switch(tabName) {
            case 'portfolio-analysis':
                this.renderPortfolioCharts();
                break;
            case 'ai-insights':
                this.loadAIInsights();
                break;
        }
    }

    nextStep(step) {
        if (this.validateCurrentStep()) {
            this.hideCurrentStep();
            this.showStep(step);
            this.updateStepIndicator(step);
            this.currentStep = step;
        }
    }

    prevStep(step) {
        this.hideCurrentStep();
        this.showStep(step);
        this.updateStepIndicator(step);
        this.currentStep = step;
    }

    validateCurrentStep() {
        const currentSection = document.getElementById(`section-${this.currentStep}`);
        const requiredFields = currentSection.querySelectorAll('[required]');
        
        for (let field of requiredFields) {
            if (!field.value.trim()) {
                field.focus();
                field.classList.add('is-invalid');
                return false;
            }
            field.classList.remove('is-invalid');
        }
        return true;
    }

    hideCurrentStep() {
        const currentSection = document.getElementById(`section-${this.currentStep}`);
        if (currentSection) {
            currentSection.classList.remove('active');
        }
    }

    showStep(step) {
        const section = document.getElementById(`section-${step}`);
        if (section) {
            section.classList.add('active');
        }
    }

    updateStepIndicator(step) {
        for (let i = 1; i <= this.totalSteps; i++) {
            const stepElement = document.getElementById(`step-${i}`);
            if (stepElement) {
                stepElement.classList.remove('active', 'completed');
                if (i < step) {
                    stepElement.classList.add('completed');
                } else if (i === step) {
                    stepElement.classList.add('active');
                }
            }
        }
    }

    async analyzeFinances() {
        try {
            // Show loading state
            this.showLoadingState();
            
            // Collect form data
            const formData = this.collectFormData();
            
            // Validate data
            if (!this.validateFormData(formData)) {
                return;
            }

            // Send to backend for analysis
            const response = await fetch('/api/analyze-finances', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                throw new Error('Analysis request failed');
            }

            const result = await response.json();
            
            if (result.success) {
                this.analysisData = result;
                this.nextStep(5);
                this.renderAnalysisResults();
            } else {
                throw new Error(result.error || 'Analysis failed');
            }

        } catch (error) {
            console.error('Analysis error:', error);
            this.showError('Failed to analyze your financial data. Please try again.');
        }
    }

    collectFormData() {
        return {
            name: document.getElementById('name').value,
            age: parseInt(document.getElementById('age').value) || 25,
            city: document.getElementById('city').value,
            familyMembers: parseInt(document.getElementById('familyMembers').value) || 1,
            salary: parseInt(document.getElementById('salary').value) || 0,
            otherIncome: parseInt(document.getElementById('otherIncome').value) || 0,
            expenses: parseInt(document.getElementById('expenses').value) || 0,
            homeLoanEmi: parseInt(document.getElementById('homeLoanEmi').value) || 0,
            carLoanEmi: parseInt(document.getElementById('carLoanEmi').value) || 0,
            otherEmis: parseInt(document.getElementById('otherEmis').value) || 0,
            creditCardDebt: parseInt(document.getElementById('creditCardDebt').value) || 0,
            currentSip: parseInt(document.getElementById('currentSip').value) || 0,
            emergencyFund: parseInt(document.getElementById('emergencyFund').value) || 0,
            hasTermInsurance: document.getElementById('hasTermInsurance').checked,
            hasHealthInsurance: document.getElementById('hasHealthInsurance').checked,
            hasLifeInsurance: document.getElementById('hasLifeInsurance').checked
        };
    }

    validateFormData(data) {
        if (!data.name || !data.age || !data.salary) {
            this.showError('Please fill in all required fields');
            return false;
        }
        return true;
    }

    showLoadingState() {
        // Add loading spinner to analysis button
        const analyzeBtn = document.querySelector('[onclick="analyzeFinances()"]');
        if (analyzeBtn) {
            analyzeBtn.innerHTML = '<span class="loading-spinner"></span> Analyzing...';
            analyzeBtn.disabled = true;
        }
    }

    renderAnalysisResults() {
        if (!this.analysisData) return;

        this.renderExecutiveSummary();
        this.renderKeyMetrics();
        this.renderPriorityActions();
        this.renderGoalPlanning();
        this.renderActionPlan();
    }

    renderExecutiveSummary() {
        const { analysis, gemini_advice } = this.analysisData;
        
        // Financial Score
        const scoreSection = document.getElementById('financial-score-section');
        if (scoreSection && gemini_advice && gemini_advice.executive_summary) {
            const { financial_health_score, wealth_category, key_strengths, priority_areas } = gemini_advice.executive_summary;
            
            scoreSection.innerHTML = `
                <div class="row align-items-center mb-4">
                    <div class="col-lg-4">
                        <div class="wealth-metric text-center">
                            <div class="metric-value">${financial_health_score}/100</div>
                            <h6 class="mb-0">Financial Health Score</h6>
                            <span class="badge ${this.getScoreBadgeClass(financial_health_score)}">${wealth_category}</span>
                        </div>
                    </div>
                    <div class="col-lg-8">
                        <div class="row">
                            <div class="col-md-6">
                                <h6><i class="fas fa-thumbs-up text-success me-2"></i>Key Strengths</h6>
                                <ul class="list-unstyled">
                                    ${key_strengths.map(strength => `<li><i class="fas fa-check text-success me-2"></i>${strength}</li>`).join('')}
                                </ul>
                            </div>
                            <div class="col-md-6">
                                <h6><i class="fas fa-exclamation-triangle text-warning me-2"></i>Priority Areas</h6>
                                <ul class="list-unstyled">
                                    ${priority_areas.map(area => `<li><i class="fas fa-arrow-right text-warning me-2"></i>${area}</li>`).join('')}
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    renderKeyMetrics() {
        const { analysis } = this.analysisData;
        
        const metricsSection = document.getElementById('key-metrics-section');
        if (metricsSection) {
            metricsSection.innerHTML = `
                <div class="row">
                    <div class="col-lg-3 col-md-6 mb-3">
                        <div class="wealth-metric">
                            <div class="metric-value">${analysis.savings_rate}%</div>
                            <p class="mb-0">Savings Rate</p>
                            <small class="text-muted">Target: 20%+</small>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6 mb-3">
                        <div class="wealth-metric">
                            <div class="metric-value">${analysis.debt_ratio}%</div>
                            <p class="mb-0">Debt Ratio</p>
                            <small class="text-muted">Target: <40%</small>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6 mb-3">
                        <div class="wealth-metric">
                            <div class="metric-value">${analysis.emergency_months}</div>
                            <p class="mb-0">Emergency Months</p>
                            <small class="text-muted">Target: 6 months</small>
                        </div>
                    </div>
                    <div class="col-lg-3 col-md-6 mb-3">
                        <div class="wealth-metric">
                            <div class="metric-value">${analysis.investment_rate}%</div>
                            <p class="mb-0">Investment Rate</p>
                            <small class="text-muted">Target: 15%+</small>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    renderPriorityActions() {
        const { recommendations } = this.analysisData;
        
        const actionsSection = document.getElementById('priority-actions');
        if (actionsSection && recommendations) {
            const priorityRecs = recommendations.slice(0, 3); // Top 3 recommendations
            
            actionsSection.innerHTML = priorityRecs.map(rec => `
                <div class="action-item">
                    <h6 class="mb-2">${rec.title}</h6>
                    <p class="mb-1 small">${rec.content}</p>
                    <p class="mb-0 text-primary small"><strong>${rec.action}</strong></p>
                </div>
            `).join('');
        }
    }

    renderPortfolioCharts() {
        if (!this.analysisData || !this.analysisData.gemini_advice) return;

        const advice = this.analysisData.gemini_advice;
        
        // Current Allocation Chart
        if (advice.detailed_portfolio_analysis && advice.detailed_portfolio_analysis.current_asset_allocation) {
            this.renderAllocationChart('current-allocation-chart', advice.detailed_portfolio_analysis.current_asset_allocation, 'Current Portfolio');
        }

        // Recommended Allocation Chart
        if (advice.detailed_portfolio_analysis && advice.detailed_portfolio_analysis.recommended_allocation) {
            this.renderAllocationChart('recommended-allocation-chart', advice.detailed_portfolio_analysis.recommended_allocation, 'Recommended Portfolio');
        }

        // Rebalancing Strategy
        const strategySection = document.getElementById('rebalancing-strategy');
        if (strategySection && advice.detailed_portfolio_analysis) {
            strategySection.innerHTML = `
                <div class="alert alert-info">
                    <h6><i class="fas fa-lightbulb me-2"></i>Strategy</h6>
                    <p class="mb-0">${advice.detailed_portfolio_analysis.rebalancing_strategy}</p>
                </div>
            `;
        }
    }

    renderAllocationChart(canvasId, data, title) {
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        // Destroy existing chart if it exists
        if (this.charts[canvasId]) {
            this.charts[canvasId].destroy();
        }

        const labels = Object.keys(data);
        const values = Object.values(data);
        const colors = ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'];

        this.charts[canvasId] = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels.map(label => label.replace('_', ' ').toUpperCase()),
                datasets: [{
                    data: values,
                    backgroundColor: colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    title: {
                        display: true,
                        text: title,
                        font: { size: 16, weight: 'bold' }
                    },
                    legend: {
                        position: 'bottom',
                        labels: { usePointStyle: true }
                    }
                }
            }
        });
    }

    renderGoalPlanning() {
        const { gemini_advice } = this.analysisData;
        if (!gemini_advice || !gemini_advice.goal_based_planning) return;

        // Short-term goals
        const shortTermSection = document.getElementById('short-term-goals');
        if (shortTermSection && gemini_advice.goal_based_planning.short_term_goals) {
            shortTermSection.innerHTML = gemini_advice.goal_based_planning.short_term_goals.map(goal => `
                <div class="investment-card">
                    <h6>${goal.goal}</h6>
                    <div class="d-flex justify-content-between mb-2">
                        <span>Target Amount:</span>
                        <strong>₹${this.formatNumber(goal.target_amount)}</strong>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                        <span>Time Horizon:</span>
                        <span>${goal.time_horizon}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                        <span>Monthly Investment:</span>
                        <strong class="text-primary">₹${this.formatNumber(goal.monthly_investment)}</strong>
                    </div>
                    <div class="mt-3">
                        <small class="text-muted">Suggested Instruments:</small>
                        <div class="mt-1">
                            ${goal.suggested_instruments.map(instrument => 
                                `<span class="badge bg-light text-dark me-1">${instrument}</span>`
                            ).join('')}
                        </div>
                    </div>
                </div>
            `).join('');
        }

        // Long-term goals
        const longTermSection = document.getElementById('long-term-goals');
        if (longTermSection && gemini_advice.goal_based_planning.long_term_goals) {
            longTermSection.innerHTML = gemini_advice.goal_based_planning.long_term_goals.map(goal => `
                <div class="investment-card">
                    <h6>${goal.goal}</h6>
                    <div class="d-flex justify-content-between mb-2">
                        <span>Target Amount:</span>
                        <strong>₹${this.formatNumber(goal.target_amount)}</strong>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                        <span>Time Horizon:</span>
                        <span>${goal.time_horizon}</span>
                    </div>
                    <div class="d-flex justify-content-between mb-2">
                        <span>Monthly SIP:</span>
                        <strong class="text-primary">₹${this.formatNumber(goal.monthly_sip)}</strong>
                    </div>
                    <div class="mt-3">
                        <small class="text-muted">Strategy:</small>
                        <p class="small mt-1">${goal.investment_strategy}</p>
                    </div>
                </div>
            `).join('');
        }

        // Wealth Milestones
        const milestonesSection = document.getElementById('wealth-milestones');
        if (milestonesSection && gemini_advice.performance_benchmarks && gemini_advice.performance_benchmarks.wealth_milestones) {
            milestonesSection.innerHTML = gemini_advice.performance_benchmarks.wealth_milestones.map(milestone => `
                <div class="investment-card">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${milestone.milestone}</h6>
                            <small class="text-muted">Target: ${milestone.target_date}</small>
                        </div>
                        <div class="text-end">
                            <div class="text-primary fw-bold">₹${this.formatNumber(milestone.required_monthly_investment)}/month</div>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    }

    renderActionPlan() {
        const { gemini_advice } = this.analysisData;
        if (!gemini_advice || !gemini_advice.monthly_action_plan) return;

        // Immediate Actions
        const immediateSection = document.getElementById('immediate-actions');
        if (immediateSection && gemini_advice.monthly_action_plan.immediate_actions) {
            immediateSection.innerHTML = gemini_advice.monthly_action_plan.immediate_actions.map((action, index) => `
                <div class="action-item">
                    <div class="d-flex align-items-center">
                        <div class="badge bg-primary me-3">${index + 1}</div>
                        <span>${action}</span>
                    </div>
                </div>
            `).join('');
        }

        // Quarterly Reviews
        const quarterlySection = document.getElementById('quarterly-reviews');
        if (quarterlySection && gemini_advice.monthly_action_plan.quarterly_reviews) {
            quarterlySection.innerHTML = gemini_advice.monthly_action_plan.quarterly_reviews.map(review => `
                <div class="action-item">
                    <i class="fas fa-calendar-check text-warning me-2"></i>
                    ${review}
                </div>
            `).join('');
        }

        // Annual Planning
        const annualSection = document.getElementById('annual-planning');
        if (annualSection && gemini_advice.monthly_action_plan.annual_planning) {
            annualSection.innerHTML = gemini_advice.monthly_action_plan.annual_planning.map(plan => `
                <div class="action-item">
                    <i class="fas fa-chart-line text-success me-2"></i>
                    ${plan}
                </div>
            `).join('');
        }

        // SIP Strategy
        const sipSection = document.getElementById('sip-strategy');
        if (sipSection && gemini_advice.monthly_action_plan.automated_investments && gemini_advice.monthly_action_plan.automated_investments.recommended_sips) {
            sipSection.innerHTML = gemini_advice.monthly_action_plan.automated_investments.recommended_sips.map(sip => `
                <div class="investment-card">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <h6 class="mb-0">${sip.fund_category}</h6>
                        <span class="badge bg-primary">₹${this.formatNumber(sip.amount)}/month</span>
                    </div>
                    <p class="small text-muted mb-0">${sip.rationale}</p>
                </div>
            `).join('');
        }
    }

    async loadAIInsights() {
        const aiContent = document.getElementById('ai-analysis-content');
        const detailedInsights = document.getElementById('detailed-ai-insights');
        
        if (!this.analysisData || !this.analysisData.gemini_advice) {
            aiContent.innerHTML = '<p class="text-center text-muted">No AI analysis available</p>';
            return;
        }

        const advice = this.analysisData.gemini_advice;

        // Main AI Analysis
        aiContent.innerHTML = `
            <div class="row">
                <div class="col-md-6">
                    <h5><i class="fas fa-user-tie me-2"></i>Risk Profile</h5>
                    <span class="risk-badge ${this.getRiskClass(advice.risk_management?.risk_profile || 'MODERATE')}">${advice.risk_management?.risk_profile || 'MODERATE'}</span>
                    <div class="mt-3">
                        <small class="text-white-50">Diversification Score</small>
                        <div class="progress mt-1" style="height: 8px;">
                            <div class="progress-bar bg-warning" style="width: ${(advice.risk_management?.diversification_score || 6) * 10}%"></div>
                        </div>
                        <small class="text-white-50">${advice.risk_management?.diversification_score || 6}/10</small>
                    </div>
                </div>
                <div class="col-md-6">
                    <h5><i class="fas fa-chart-line me-2"></i>Projected Wealth (10 years)</h5>
                    <div class="metric-value text-white">₹${this.formatNumber(advice.executive_summary?.projected_wealth_10yr || 0)}</div>
                    <small class="text-white-50">With recommended strategy</small>
                </div>
            </div>
        `;

        // Detailed Insights
        detailedInsights.innerHTML = `
            <div class="row mt-4">
                <div class="col-lg-6 mb-4">
                    <div class="professional-card p-4">
                        <h5><i class="fas fa-shield-alt me-2"></i>Risk Management</h5>
                        ${this.renderInsuranceGapAnalysis(advice.risk_management)}
                    </div>
                </div>
                <div class="col-lg-6 mb-4">
                    <div class="professional-card p-4">
                        <h5><i class="fas fa-calculator me-2"></i>Tax Optimization</h5>
                        ${this.renderTaxOptimization(advice.tax_optimization)}
                    </div>
                </div>
                <div class="col-12">
                    <div class="professional-card p-4">
                        <h5><i class="fas fa-chart-bar me-2"></i>Market Outlook & Strategy</h5>
                        ${this.renderMarketOutlook(advice.market_outlook_advisory)}
                    </div>
                </div>
            </div>
        `;
    }

    renderInsuranceGapAnalysis(riskManagement) {
        if (!riskManagement || !riskManagement.insurance_gap_analysis) {
            return '<p class="text-muted">No insurance analysis available</p>';
        }

        const gap = riskManagement.insurance_gap_analysis;
        return `
            <div class="row">
                <div class="col-6">
                    <div class="text-center p-3 bg-light rounded">
                        <div class="h6 text-primary">₹${this.formatNumber(gap.life_cover_needed)}</div>
                        <small>Life Cover Needed</small>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-center p-3 bg-light rounded">
                        <div class="h6 text-primary">₹${this.formatNumber(gap.health_cover_needed)}</div>
                        <small>Health Cover Needed</small>
                    </div>
                </div>
            </div>
            <div class="mt-3">
                <p class="small">Annual Premium Budget: <strong>₹${this.formatNumber(gap.annual_premium_budget)}</strong></p>
                ${riskManagement.concentration_risks ? `
                    <div class="mt-2">
                        <small class="text-muted">Key Risks:</small>
                        <div>${riskManagement.concentration_risks.map(risk => `<span class="badge bg-warning me-1">${risk}</span>`).join('')}</div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    renderTaxOptimization(taxOptimization) {
        if (!taxOptimization) {
            return '<p class="text-muted">No tax optimization data available</p>';
        }

        return `
            <div class="row mb-3">
                <div class="col-6">
                    <div class="text-center p-3 bg-light rounded">
                        <div class="h6 text-danger">₹${this.formatNumber(taxOptimization.current_tax_liability || 0)}</div>
                        <small>Current Tax</small>
                    </div>
                </div>
                <div class="col-6">
                    <div class="text-center p-3 bg-light rounded">
                        <div class="h6 text-success">₹${this.formatNumber(taxOptimization.potential_savings || 0)}</div>
                        <small>Potential Savings</small>
                    </div>
                </div>
            </div>
            ${taxOptimization.tax_efficient_instruments ? `
                <div class="mt-3">
                    <small class="text-muted">Recommended Instruments:</small>
                    ${taxOptimization.tax_efficient_instruments.map(instrument => `
                        <div class="mt-2 p-2 bg-light rounded">
                            <div class="d-flex justify-content-between">
                                <strong>${instrument.instrument}</strong>
                                <span class="text-primary">₹${this.formatNumber(instrument.recommended_amount)}</span>
                            </div>
                            <small class="text-muted">${instrument.tax_benefit} • Expected: ${instrument.expected_returns}%</small>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        `;
    }

    renderMarketOutlook(marketOutlook) {
        if (!marketOutlook) {
            return '<p class="text-muted">No market outlook available</p>';
        }

        return `
            <div class="row">
                <div class="col-md-8">
                    <h6>Current Market View</h6>
                    <p>${marketOutlook.current_market_view}</p>
                    
                    ${marketOutlook.sector_opportunities ? `
                        <h6 class="mt-3">Sector Opportunities</h6>
                        <div>
                            ${marketOutlook.sector_opportunities.map(sector => 
                                `<span class="badge bg-success me-2 mb-1">${sector}</span>`
                            ).join('')}
                        </div>
                    ` : ''}
                </div>
                <div class="col-md-4">
                    ${marketOutlook.timing_strategies ? `
                        <h6>Timing Strategies</h6>
                        <div class="small">
                            <p><strong>SIP Timing:</strong> ${marketOutlook.timing_strategies.sip_timing}</p>
                            <p><strong>Lumpsum:</strong> ${marketOutlook.timing_strategies.lumpsum_opportunities}</p>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }

    getScoreBadgeClass(score) {
        if (score >= 80) return 'badge bg-success';
        if (score >= 60) return 'badge bg-warning';
        return 'badge bg-danger';
    }

    getRiskClass(riskLevel) {
        switch(riskLevel) {
            case 'CONSERVATIVE': return 'risk-low';
            case 'MODERATE': return 'risk-medium';
            case 'AGGRESSIVE': return 'risk-high';
            default: return 'risk-medium';
        }
    }

    formatNumber(num) {
        if (!num) return '0';
        if (num >= 10000000) return (num / 10000000).toFixed(1) + ' Cr';
        if (num >= 100000) return (num / 100000).toFixed(1) + ' L';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toLocaleString('en-IN');
    }

    showError(message) {
        alert(message); // You can replace this with a better error display
    }
}

// Global functions for HTML onclick events
let advisor = new ProfessionalFinancialAdvisor();

function nextStep(step) {
    advisor.nextStep(step);
}

function prevStep(step) {
    advisor.prevStep(step);
}

function analyzeFinances() {
    advisor.analyzeFinances();
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Professional Financial Advisor initialized');
});
