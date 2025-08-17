// Financial Advisor JavaScript
class FinancialAdvisor {
    constructor() {
        this.currentStep = 1;
        this.totalSteps = 4;
        this.financialData = {};
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Tab switching
        document.querySelectorAll('[data-bs-toggle="pill"]').forEach(tab => {
            tab.addEventListener('shown.bs.tab', (e) => {
                if (e.target.id === 'analysis-tab' || e.target.id === 'recommendations-tab') {
                    this.calculateFinancialHealth();
                }
            });
        });
    }

    changeStep(direction) {
        const currentStepEl = document.getElementById(`step${this.currentStep}`);
        
        if (direction === 1) {
            // Validate current step
            if (!this.validateStep(this.currentStep)) {
                return;
            }
            
            this.currentStep++;
            if (this.currentStep > this.totalSteps) {
                this.completeForm();
                return;
            }
        } else {
            this.currentStep--;
            if (this.currentStep < 1) {
                this.currentStep = 1;
                return;
            }
        }

        // Hide all steps
        document.querySelectorAll('.form-step').forEach(step => {
            step.classList.remove('active');
        });

        // Show current step
        document.getElementById(`step${this.currentStep}`).classList.add('active');

        // Update progress
        const progress = (this.currentStep / this.totalSteps) * 100;
        document.getElementById('progressBar').style.width = `${progress}%`;

        // Update buttons
        document.getElementById('prevBtn').style.display = this.currentStep === 1 ? 'none' : 'inline-block';
        document.getElementById('nextBtn').textContent = this.currentStep === this.totalSteps ? 'Analyze Finances' : 'Next';
    }

    validateStep(step) {
        const stepEl = document.getElementById(`step${step}`);
        const requiredFields = stepEl.querySelectorAll('[required]');
        
        for (let field of requiredFields) {
            if (!field.value.trim()) {
                field.focus();
                this.showAlert('Please fill all required fields', 'warning');
                return false;
            }
        }
        return true;
    }

    completeForm() {
        this.collectFormData();
        this.calculateFinancialHealth();
        
        // Switch to analysis tab
        const analysisTab = new bootstrap.Tab(document.getElementById('analysis-tab'));
        analysisTab.show();
        
        this.showAlert('Financial analysis completed!', 'success');
    }

    collectFormData() {
        this.financialData = {
            name: document.getElementById('name').value,
            age: parseInt(document.getElementById('age').value),
            city: document.getElementById('city').value,
            familyMembers: parseInt(document.getElementById('familyMembers').value),
            salary: parseInt(document.getElementById('salary').value),
            otherIncome: parseInt(document.getElementById('otherIncome').value) || 0,
            incomeSource: document.getElementById('incomeSource').value,
            expenses: parseInt(document.getElementById('expenses').value),
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

    calculateFinancialHealth() {
        if (!this.financialData.salary) return;

        const data = this.financialData;
        const totalIncome = data.salary + data.otherIncome;
        const totalEmis = data.homeLoanEmi + data.carLoanEmi + data.otherEmis;
        const totalExpenses = data.expenses + totalEmis;
        
        // Calculate metrics
        const savingsAmount = totalIncome - totalExpenses;
        const savingsRate = (savingsAmount / totalIncome) * 100;
        const debtRatio = (totalEmis / totalIncome) * 100;
        const emergencyMonths = data.emergencyFund / data.expenses;
        const investmentRate = (data.currentSip / totalIncome) * 100;

        // Calculate financial score (0-100)
        let score = 0;
        
        // Savings rate (30 points)
        if (savingsRate >= 20) score += 30;
        else if (savingsRate >= 15) score += 25;
        else if (savingsRate >= 10) score += 20;
        else if (savingsRate >= 5) score += 15;
        else score += 10;

        // Debt ratio (25 points)
        if (debtRatio <= 30) score += 25;
        else if (debtRatio <= 40) score += 20;
        else if (debtRatio <= 50) score += 15;
        else score += 10;

        // Emergency fund (20 points)
        if (emergencyMonths >= 6) score += 20;
        else if (emergencyMonths >= 3) score += 15;
        else if (emergencyMonths >= 1) score += 10;
        else score += 5;

        // Insurance coverage (15 points)
        let insuranceScore = 0;
        if (data.hasTermInsurance) insuranceScore += 5;
        if (data.hasHealthInsurance) insuranceScore += 5;
        if (data.hasLifeInsurance) insuranceScore += 5;
        score += insuranceScore;

        // Investment rate (10 points)
        if (investmentRate >= 15) score += 10;
        else if (investmentRate >= 10) score += 8;
        else if (investmentRate >= 5) score += 6;
        else score += 3;

        // Update UI
        this.updateFinancialMetrics(score, savingsRate, debtRatio, emergencyMonths, investmentRate);
        this.generate502030Analysis(totalIncome, totalExpenses, savingsAmount);
        this.generateRecommendations(score, data, totalIncome, savingsAmount);
    }

    updateFinancialMetrics(score, savingsRate, debtRatio, emergencyMonths, investmentRate) {
        document.getElementById('financialScore').textContent = Math.round(score);
        document.getElementById('savingsRate').textContent = `${Math.round(savingsRate)}%`;
        document.getElementById('debtRatio').textContent = `${Math.round(debtRatio)}%`;
        document.getElementById('emergencyMonths').textContent = `${emergencyMonths.toFixed(1)} months`;
        document.getElementById('investmentRate').textContent = `${Math.round(investmentRate)}%`;

        // Update additional metrics
        document.getElementById('debtToIncomeRatio').textContent = `${Math.round(debtRatio)}%`;
        document.getElementById('emergencyFundCoverage').textContent = `${emergencyMonths.toFixed(1)} months`;
        document.getElementById('investmentAllocation').textContent = `${Math.round(investmentRate)}%`;

        // Update insurance status
        const data = this.financialData;
        document.getElementById('termInsuranceStatus').textContent = data.hasTermInsurance ? '✓ Covered' : '✗ Not Covered';
        document.getElementById('termInsuranceStatus').className = `badge ${data.hasTermInsurance ? 'bg-success' : 'bg-danger'}`;
        
        document.getElementById('healthInsuranceStatus').textContent = data.hasHealthInsurance ? '✓ Covered' : '✗ Not Covered';
        document.getElementById('healthInsuranceStatus').className = `badge ${data.hasHealthInsurance ? 'bg-success' : 'bg-danger'}`;
        
        document.getElementById('lifeInsuranceStatus').textContent = data.hasLifeInsurance ? '✓ Covered' : '✗ Not Covered';
        document.getElementById('lifeInsuranceStatus').className = `badge ${data.hasLifeInsurance ? 'bg-success' : 'bg-danger'}`;

        // Score description
        let description = '';
        if (score >= 80) description = 'Excellent financial health!';
        else if (score >= 60) description = 'Good financial health';
        else if (score >= 40) description = 'Fair financial health';
        else description = 'Needs improvement';

        document.getElementById('scoreDescription').textContent = description;
    }

    generate502030Analysis(totalIncome, totalExpenses, savingsAmount) {
        const ideal50 = totalIncome * 0.5; // Needs
        const ideal30 = totalIncome * 0.3; // Wants
        const ideal20 = totalIncome * 0.2; // Savings

        const actualNeeds = totalExpenses > ideal50 ? ideal50 : totalExpenses;
        const actualWants = totalExpenses > ideal50 ? totalExpenses - ideal50 : 0;
        const actualSavings = savingsAmount;

        // Calculate percentages for progress bars
        const needsPercent = (actualNeeds / totalIncome) * 100;
        const wantsPercent = (actualWants / totalIncome) * 100;
        const savingsPercent = (actualSavings / totalIncome) * 100;

        // Update progress bars
        document.getElementById('needsProgress').style.width = `${needsPercent}%`;
        document.getElementById('needsProgress').textContent = `${Math.round(needsPercent)}%`;

        document.getElementById('wantsProgress').style.width = `${wantsPercent}%`;
        document.getElementById('wantsProgress').textContent = `${Math.round(wantsPercent)}%`;

        document.getElementById('savingsProgress').style.width = `${savingsPercent}%`;
        document.getElementById('savingsProgress').textContent = `${Math.round(savingsPercent)}%`;
    }

    generateRecommendations(score, data, totalIncome, savingsAmount) {
        const recommendations = [];

        // Budget recommendations
        if (savingsAmount < totalIncome * 0.2) {
            recommendations.push({
                type: 'budget',
                title: 'Improve Your Savings Rate',
                icon: 'fas fa-piggy-bank',
                content: `Your current savings rate is ${Math.round((savingsAmount/totalIncome)*100)}%. Aim for at least 20% savings rate by reducing non-essential expenses.`,
                action: 'Create a detailed budget and track your expenses for the next 3 months.'
            });
        }

        // Debt management
        const totalEmis = data.homeLoanEmi + data.carLoanEmi + data.otherEmis;
        if (totalEmis > totalIncome * 0.4) {
            recommendations.push({
                type: 'debt',
                title: 'Reduce Debt Burden',
                icon: 'fas fa-credit-card',
                content: `Your EMI-to-income ratio is ${Math.round((totalEmis/totalIncome)*100)}%. This is higher than the recommended 40%.`,
                action: 'Consider debt consolidation or prepaying high-interest loans to reduce monthly burden.'
            });
        }

        // Emergency fund
        const emergencyMonths = data.emergencyFund / data.expenses;
        if (emergencyMonths < 6) {
            recommendations.push({
                type: 'budget',
                title: 'Build Emergency Fund',
                icon: 'fas fa-umbrella',
                content: `You have ${emergencyMonths.toFixed(1)} months of expenses as emergency fund. Aim for 6 months.`,
                action: `Save ₹${Math.round((6 * data.expenses - data.emergencyFund)/12)} monthly to reach your goal in 12 months.`
            });
        }

        // Insurance recommendations
        if (!data.hasTermInsurance) {
            const termCover = totalIncome * 12 * 10; // 10x annual income
            recommendations.push({
                type: 'insurance',
                title: 'Get Term Insurance',
                icon: 'fas fa-shield-alt',
                content: `Term insurance is essential for financial security. Get coverage of ₹${(termCover/10000000).toFixed(1)} crores.`,
                action: `Premium: Approximately ₹${Math.round(termCover * 0.0005/12)} per month for ₹${(termCover/10000000).toFixed(1)} crores coverage.`
            });
        }

        if (!data.hasHealthInsurance) {
            const healthCover = data.familyMembers * 500000; // 5L per person
            recommendations.push({
                type: 'insurance',
                title: 'Get Health Insurance',
                icon: 'fas fa-heartbeat',
                content: `Health insurance is crucial for medical emergencies. Get family coverage of ₹${healthCover/100000} lakhs.`,
                action: `Premium: Approximately ₹${Math.round(healthCover * 0.03/12)} per month for family coverage.`
            });
        }

        // Investment recommendations
        if (data.currentSip < totalIncome * 0.15) {
            const recommendedSip = totalIncome * 0.15;
            recommendations.push({
                type: 'investment',
                title: 'Increase SIP Investments',
                icon: 'fas fa-chart-line',
                content: `Your current SIP is ₹${data.currentSip}. Increase to ₹${Math.round(recommendedSip)} (15% of income) for wealth creation.`,
                action: `Start with equity mutual funds through SIP. Expected returns: 12-15% annually over long term.`
            });
        }

        // Tax savings
        recommendations.push({
            type: 'investment',
            title: 'Tax Saving Investments',
            icon: 'fas fa-receipt',
            content: 'Maximize tax benefits under Section 80C and other provisions.',
            action: 'Invest in ELSS mutual funds, PPF, and claim HRA/home loan interest to save taxes.'
        });

        // Generate recommendations HTML
        this.renderRecommendations(recommendations);
    }

    renderRecommendations(recommendations) {
        const container = document.getElementById('recommendationsContent');
        
        if (recommendations.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="fas fa-trophy fa-3x text-success mb-3"></i>
                    <h4 class="text-success">Excellent Financial Health!</h4>
                    <p>You're doing great with your financial planning. Keep it up!</p>
                </div>
            `;
            return;
        }

        let html = `
            <div class="row mb-4">
                <div class="col-12">
                    <h3 class="text-center mb-4">
                        <i class="fas fa-lightbulb me-2 text-warning"></i>
                        Personalized Financial Recommendations
                    </h3>
                </div>
            </div>
        `;

        recommendations.forEach(rec => {
            html += `
                <div class="advice-card ${rec.type}">
                    <div class="d-flex align-items-start">
                        <div class="me-3">
                            <i class="${rec.icon} fa-2x text-primary"></i>
                        </div>
                        <div class="flex-grow-1">
                            <h5 class="fw-bold">${rec.title}</h5>
                            <p class="mb-2">${rec.content}</p>
                            <div class="alert alert-light mb-0">
                                <strong>Action Plan:</strong> ${rec.action}
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });

        // Add general wealth building tips
        html += `
            <div class="row mt-4">
                <div class="col-12">
                    <div class="card bg-light">
                        <div class="card-header">
                            <h5><i class="fas fa-coins me-2"></i>Wealth Building Tips</h5>
                        </div>
                        <div class="card-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <ul class="list-unstyled">
                                        <li><i class="fas fa-check text-success me-2"></i>Start SIP early to benefit from compounding</li>
                                        <li><i class="fas fa-check text-success me-2"></i>Diversify across equity, debt, and gold</li>
                                        <li><i class="fas fa-check text-success me-2"></i>Review and rebalance portfolio annually</li>
                                    </ul>
                                </div>
                                <div class="col-md-6">
                                    <ul class="list-unstyled">
                                        <li><i class="fas fa-check text-success me-2"></i>Increase SIP amount with salary hikes</li>
                                        <li><i class="fas fa-check text-success me-2"></i>Consider ELSS for tax saving</li>
                                        <li><i class="fas fa-check text-success me-2"></i>Stay invested for long-term goals</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        const container = document.querySelector('.container');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
}

// SIP Calculator Functions
let sipChart = null;

function calculateSIP() {
    const sipAmount = parseInt(document.getElementById('sipAmount').value);
    const sipPeriod = parseInt(document.getElementById('sipPeriod').value);
    const sipReturn = parseFloat(document.getElementById('sipReturn').value);
    const stepUpSip = document.getElementById('stepUpSip').checked;
    const stepUpPercent = stepUpSip ? parseFloat(document.getElementById('stepUpPercent').value) : 0;

    if (!sipAmount || !sipPeriod || !sipReturn) {
        alert('Please fill all SIP calculator fields');
        return;
    }

    let results;
    if (stepUpSip) {
        results = calculateStepUpSIP(sipAmount, sipPeriod, sipReturn, stepUpPercent);
    } else {
        results = calculateRegularSIP(sipAmount, sipPeriod, sipReturn);
    }

    displaySIPResults(results);
    createSIPChart(results);
}

function calculateRegularSIP(monthlyAmount, years, annualReturn) {
    const months = years * 12;
    const monthlyReturn = annualReturn / 100 / 12;
    
    // SIP Future Value Formula: P * (((1 + r)^n - 1) / r) * (1 + r)
    const futureValue = monthlyAmount * (((Math.pow(1 + monthlyReturn, months) - 1) / monthlyReturn) * (1 + monthlyReturn));
    const totalInvestment = monthlyAmount * months;
    const totalGains = futureValue - totalInvestment;

    return {
        futureValue: Math.round(futureValue),
        totalInvestment: totalInvestment,
        totalGains: Math.round(totalGains),
        monthlyAmount: monthlyAmount,
        years: years,
        annualReturn: annualReturn,
        type: 'regular'
    };
}

function calculateStepUpSIP(initialAmount, years, annualReturn, stepUpPercent) {
    const monthlyReturn = annualReturn / 100 / 12;
    let totalInvestment = 0;
    let futureValue = 0;
    let currentMonthlyAmount = initialAmount;

    for (let year = 1; year <= years; year++) {
        const monthsInYear = 12;
        const yearlyInvestment = currentMonthlyAmount * monthsInYear;
        totalInvestment += yearlyInvestment;

        // Calculate future value for this year's investments
        const remainingYears = years - year + 1;
        const remainingMonths = remainingYears * 12;
        const yearFV = currentMonthlyAmount * (((Math.pow(1 + monthlyReturn, remainingMonths) - 1) / monthlyReturn) * (1 + monthlyReturn));
        futureValue += yearFV;

        // Increase amount for next year
        currentMonthlyAmount = Math.round(currentMonthlyAmount * (1 + stepUpPercent / 100));
    }

    return {
        futureValue: Math.round(futureValue),
        totalInvestment: totalInvestment,
        totalGains: Math.round(futureValue - totalInvestment),
        monthlyAmount: initialAmount,
        years: years,
        annualReturn: annualReturn,
        stepUpPercent: stepUpPercent,
        type: 'stepup'
    };
}

function displaySIPResults(results) {
    const resultsDiv = document.getElementById('sipResults');
    
    const html = `
        <div class="row g-3">
            <div class="col-12">
                <div class="alert alert-info">
                    <h6 class="mb-2"><i class="fas fa-calculator me-2"></i>SIP Calculation Results</h6>
                    <p class="mb-0 small">${results.type === 'stepup' ? 'Step-up' : 'Regular'} SIP for ${results.years} years @ ${results.annualReturn}% annual return</p>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card bg-primary">
                    <div class="metric-value">₹${(results.futureValue / 10000000).toFixed(2)}Cr</div>
                    <div class="metric-label">Maturity Amount</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card bg-success">
                    <div class="metric-value">₹${(results.totalInvestment / 100000).toFixed(1)}L</div>
                    <div class="metric-label">Total Investment</div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="metric-card bg-warning">
                    <div class="metric-value">₹${(results.totalGains / 10000000).toFixed(2)}Cr</div>
                    <div class="metric-label">Total Gains</div>
                </div>
            </div>
            <div class="col-12">
                <div class="card bg-light">
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-6">
                                <h6>Return on Investment</h6>
                                <h4 class="text-success">${((results.totalGains / results.totalInvestment) * 100).toFixed(1)}%</h4>
                            </div>
                            <div class="col-6">
                                <h6>Wealth Multiplier</h6>
                                <h4 class="text-primary">${(results.futureValue / results.totalInvestment).toFixed(1)}x</h4>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

function createSIPChart(results) {
    const ctx = document.getElementById('sipChart').getContext('2d');
    
    if (sipChart) {
        sipChart.destroy();
    }

    const years = results.years;
    const labels = [];
    const investmentData = [];
    const valueData = [];
    
    for (let year = 1; year <= years; year++) {
        labels.push(`Year ${year}`);
        
        if (results.type === 'stepup') {
            // Step-up SIP calculation per year
            let yearlyInvestment = 0;
            let currentAmount = results.monthlyAmount;
            for (let y = 1; y <= year; y++) {
                yearlyInvestment += currentAmount * 12;
                if (y < year) currentAmount *= (1 + results.stepUpPercent / 100);
            }
            investmentData.push(yearlyInvestment);
        } else {
            investmentData.push(results.monthlyAmount * 12 * year);
        }
        
        // Calculate compound growth for value
        const monthlyReturn = results.annualReturn / 100 / 12;
        const months = year * 12;
        const yearValue = results.monthlyAmount * (((Math.pow(1 + monthlyReturn, months) - 1) / monthlyReturn) * (1 + monthlyReturn));
        valueData.push(yearValue);
    }

    sipChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Total Investment',
                data: investmentData,
                borderColor: '#007bff',
                backgroundColor: 'rgba(0, 123, 255, 0.1)',
                fill: true
            }, {
                label: 'Portfolio Value',
                data: valueData,
                borderColor: '#28a745',
                backgroundColor: 'rgba(40, 167, 69, 0.1)',
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '₹' + (value / 100000).toFixed(1) + 'L';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'top',
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ₹' + (context.parsed.y / 100000).toFixed(1) + 'L';
                        }
                    }
                }
            }
        }
    });
}

// Range slider synchronization
function initializeSIPCalculator() {
    // SIP Amount synchronization
    const sipAmount = document.getElementById('sipAmount');
    const sipPeriod = document.getElementById('sipPeriod');
    const sipPeriodRange = document.getElementById('sipPeriodRange');
    const sipReturn = document.getElementById('sipReturn');
    const sipReturnRange = document.getElementById('sipReturnRange');
    const stepUpSip = document.getElementById('stepUpSip');
    const stepUpSection = document.getElementById('stepUpSection');

    // Synchronize range sliders with input fields
    sipPeriodRange.addEventListener('input', function() {
        sipPeriod.value = this.value;
        calculateSIP();
    });

    sipPeriod.addEventListener('input', function() {
        sipPeriodRange.value = this.value;
        calculateSIP();
    });

    sipReturnRange.addEventListener('input', function() {
        sipReturn.value = this.value;
        calculateSIP();
    });

    sipReturn.addEventListener('input', function() {
        sipReturnRange.value = this.value;
        calculateSIP();
    });

    sipAmount.addEventListener('input', calculateSIP);

    // Step-up SIP toggle
    stepUpSip.addEventListener('change', function() {
        stepUpSection.style.display = this.checked ? 'block' : 'none';
        calculateSIP();
    });

    document.getElementById('stepUpPercent').addEventListener('input', calculateSIP);

    // Initial calculation
    calculateSIP();
}

// Global functions for button clicks
function changeStep(direction) {
    window.financialAdvisor.changeStep(direction);
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.financialAdvisor = new FinancialAdvisor();
    
    // Initialize SIP calculator when SIP tab is shown
    document.getElementById('sip-calculator-tab').addEventListener('shown.bs.tab', function() {
        initializeSIPCalculator();
    });
});
