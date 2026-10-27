// Dashboard Chart.js Initializer

function initDashboardCharts(distributionData, courseStatsData) {
  // 1. Attendance Distribution Doughnut Chart
  const distCtx = document.getElementById('attendanceDoughnutChart');
  if (distCtx) {
    new Chart(distCtx, {
      type: 'doughnut',
      data: {
        labels: ['Present', 'Late', 'Absent'],
        datasets: [{
          data: [
            distributionData.Present || 0,
            distributionData.Late || 0,
            distributionData.Absent || 0
          ],
          backgroundColor: [
            '#10b981', // green for Present
            '#f59e0b', // amber for Late
            '#ef4444'  // red for Absent
          ],
          borderWidth: 2,
          borderColor: '#ffffff',
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              boxWidth: 14,
              padding: 16,
              font: {
                size: 13,
                weight: '500'
              }
            }
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const val = context.raw || 0;
                const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                return ` ${context.label}: ${val} (${pct}%)`;
              }
            }
          }
        },
        cutout: '68%'
      }
    });
  }

  // 2. Course-wise Attendance Bar Chart
  const courseCtx = document.getElementById('courseAttendanceBarChart');
  if (courseCtx && courseStatsData && courseStatsData.length > 0) {
    const labels = courseStatsData.map(c => c.course_code);
    const presentData = courseStatsData.map(c => c.present_count || 0);
    const lateData = courseStatsData.map(c => c.late_count || 0);
    const absentData = courseStatsData.map(c => c.absent_count || 0);

    new Chart(courseCtx, {
      type: 'bar',
      data: {
        labels: labels,
        datasets: [
          {
            label: 'Present',
            data: presentData,
            backgroundColor: '#10b981',
            borderRadius: 6
          },
          {
            label: 'Late',
            data: lateData,
            backgroundColor: '#f59e0b',
            borderRadius: 6
          },
          {
            label: 'Absent',
            data: absentData,
            backgroundColor: '#ef4444',
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            stacked: true,
            grid: { display: false }
          },
          y: {
            stacked: true,
            beginAtZero: true,
            ticks: { precision: 0 }
          }
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              boxWidth: 12,
              font: { size: 12 }
            }
          }
        }
      }
    });
  }
}
