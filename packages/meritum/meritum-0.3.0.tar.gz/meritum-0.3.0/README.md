# Meritum

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
[![PyPI](https://img.shields.io/pypi/v/meritum?color=orange)](https://pypi.org/project/meritum/)

A tool for tracking student progress using Gantt charts and task management, designed especially for academic contexts like undergraduate and Ph.D. programs.

![meritum](https://raw.githubusercontent.com/maurobedoya/meritum/main/meritum/assets/meritum_main.png)

## Features

- **Dual Mode Interface**: Separate views for teachers and students
- **Visual Progress Tracking**: Intuitive Gantt charts for project visualization
- **Goals Management**: Create and track goals with customizable colors
- **Task Management**: Create, assign, and track tasks with deadlines
- **Goal-Task Association**: Link tasks to specific goals for better organization and progress tracking
- **Progress History**: Detailed history of task completion and progress
- **Note Taking**: Add detailed notes to tasks for better context
- **Profile Management**: Keep detailed student profiles in one place

## Installation

Install Meritum easily using pip:

```bash
pip install meritum
```

Or install directly from GitHub for the latest version:

```bash
pip install git+https://github.com/maurobedoya/meritum.git
```

To update to the latest version (since we are making a lot of changes ;) ) use:

```bash
pip install --upgrade meritum
```

## Usage

After installation, simply run:

```bash
python -m meritum
```

or 
```bash
meritum
```

On first run, you'll be prompted to choose either Teacher or Student mode.
[<img align="right" src="https://raw.githubusercontent.com/maurobedoya/meritum/main/meritum/assets/meritum_select_mode.png" width="300" />](https://raw.githubusercontent.com/maurobedoya/meritum/main/meritum/assets/meritum_select_mode.png)


# Setup guide
## For Teachers

### 1. Initial setup
- Launch Meritum and select "Teacher Mode"
- Go to Settings to configure application defaults if needed
  
### 2. Add students
- Click "Add Student" in the sidebar
- Enter the student´s name and create a data folder path
- This data folder should be in a location that can be shared (Dropbox, Google Drive, OneDrive, etc.)
- Fill the student´s profile information

### 3. Share Data Folder
- Share the data folder with your student using your preferred file-sharing service

### 4. Create Goals and Tasks
- Set up initial goals for the student from the Goals tab
- Create tasks and milestones from the Tasks tab or Gantt Chart
- Assign tasks to either yourself or the student

### 5. Monitor Progress
- Use the Gantt Chart to get a visual overview of the project timeline
- Regular check-ins through the Notes feature can provide qualitative feedback

## For Students:

### 1. Initial Setup

- Launch Meritum and select "Student Mode"
- When prompted, enter the data folder path shared by your teacher
- If an existing profile exists, select it; otherwise, create a new profile

### 2. Configure Data Path

- Verify the data folder path in the Settings tab
- Make sure it points to the synchronized folder on your computer. Note that your local path may be different from your teacher's path, but both should point to the same synchronized folder (via Dropbox, Google Drive, etc.)
  
### 3. View and Update Progress

- View assigned tasks in the Tasks tab or Gantt Chart
- Update your progress on tasks by editing them and adjusting the progress percentage
- Mark tasks as complete when finished

### 4. Add Notes

- Use the Notes feature to provide context or ask questions about specific tasks
- All notes will be synchronized with your teacher

### Synchronization:

All changes are automatically saved to the shared data folder. Both teacher and student see the same real-time data. There's no need for manual synchronization as long as both parties are using the same data folder. For cloud-based sharing services (Dropbox, Google Drive, etc.), ensure that syncing is enabled and up-to-date

## Adding students

[<img align="center" src="https://raw.githubusercontent.com/maurobedoya/meritum/main/meritum/assets/meritum_add_student.png" width="800" />](https://raw.githubusercontent.com/maurobedoya/meritum/main/meritum/assets/meritum_add_student.png)


## Adding goals

[<img align="center" src="https://raw.githubusercontent.com/maurobedoya/meritum/main/meritum/assets/meritum_add_goals2.png" width="800" />](https://raw.githubusercontent.com/maurobedoya/meritum/main/meritum/assets/meritum_add_goals2.png)

## Adding tasks

[<img align="center" src="https://raw.githubusercontent.com/maurobedoya/meritum/main/meritum/assets/meritum_add_tasks.png" width="800" />](https://raw.githubusercontent.com/maurobedoya/meritum/main/meritum/assets/meritum_add_tasks.png)


## Requirements

- Python 3.7 or higher
- customtkinter 5.2.2 or higher

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Acknowledgments

- Thanks to all contributors and testers
- Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
