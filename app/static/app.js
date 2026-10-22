const taskForm = document.querySelector("#task-form");
const titleInput = document.querySelector("#title");
const descriptionInput = document.querySelector("#description");
const priorityInput = document.querySelector("#priority");
const dueDateInput = document.querySelector("#due-date");
const submitButton = document.querySelector("#submit-button");
const cancelEditButton = document.querySelector("#cancel-edit");
const formHeading = document.querySelector("#form-heading");
const formError = document.querySelector("#form-error");
const listMessage = document.querySelector("#list-message");
const taskList = document.querySelector("#task-list");
const taskCount = document.querySelector("#task-count");
const statusFilter = document.querySelector("#status-filter");
const sortOrder = document.querySelector("#sort-order");

let editingTaskId = null;
let editingTaskCompleted = false;
let requestInProgress = false;

function showFormError(message) {
  formError.textContent = message;
  formError.hidden = !message;
}

function errorMessageFrom(response, payload) {
  if (payload?.error?.details?.length) {
    return payload.error.details.map((detail) => detail.message).join(" ");
  }
  return payload?.error?.message || `Request failed (${response.status}). Please try again.`;
}

async function requestJson(url, options) {
  const response = await fetch(url, options);
  if (response.status === 204) {
    if (!response.ok) {
      throw new Error(`Request failed (${response.status}).`);
    }
    return null;
  }
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(errorMessageFrom(response, payload));
  }
  return payload;
}

function addTextElement(parent, tag, text, className) {
  const element = document.createElement(tag);
  element.textContent = text;
  if (className) {
    element.className = className;
  }
  parent.append(element);
  return element;
}

function renderTask(task) {
  const item = document.createElement("li");
  item.className = `task-card${task.completed ? " is-completed" : ""}`;

  const checkbox = document.createElement("input");
  checkbox.className = "completion-toggle";
  checkbox.type = "checkbox";
  checkbox.checked = task.completed;
  checkbox.setAttribute("aria-label", `${task.completed ? "Reopen" : "Complete"} ${task.title}`);
  checkbox.addEventListener("change", () => toggleTask(task, checkbox.checked));
  item.append(checkbox);

  const content = document.createElement("div");
  content.className = "task-content";
  addTextElement(content, "h3", task.title, "task-title");
  if (task.description) {
    addTextElement(content, "p", task.description, "task-description");
  }

  const metadata = document.createElement("div");
  metadata.className = "task-meta";
  addTextElement(metadata, "span", task.priority, `badge priority-${task.priority}`);
  if (task.due_date) {
    addTextElement(metadata, "span", `Due ${task.due_date}`);
  }
  if (task.completed) {
    addTextElement(metadata, "span", "Completed", "completed-label");
  }
  content.append(metadata);
  item.append(content);

  const actions = document.createElement("div");
  actions.className = "task-actions";
  const editButton = addTextElement(actions, "button", "Edit", "icon-button");
  editButton.type = "button";
  editButton.setAttribute("aria-label", `Edit ${task.title}`);
  editButton.addEventListener("click", () => startEditing(task));
  const deleteButton = addTextElement(actions, "button", "Delete", "icon-button delete");
  deleteButton.type = "button";
  deleteButton.setAttribute("aria-label", `Delete ${task.title}`);
  deleteButton.addEventListener("click", () => deleteTask(task));
  item.append(actions);
  return item;
}

async function loadTasks() {
  listMessage.hidden = false;
  listMessage.textContent = "Loading tasks…";
  taskList.replaceChildren();
  try {
    const parameters = new URLSearchParams({ status: statusFilter.value });
    if (sortOrder.value) {
      parameters.set("sort", sortOrder.value);
    }
    const tasks = await requestJson(`/api/tasks?${parameters}`);
    taskCount.textContent = `(${tasks.length})`;
    if (tasks.length === 0) {
      listMessage.textContent = statusFilter.value === "all"
        ? "No tasks yet. Add one to get started."
        : `No ${statusFilter.value} tasks to show.`;
      return;
    }
    listMessage.hidden = true;
    const fragment = document.createDocumentFragment();
    tasks.forEach((task) => fragment.append(renderTask(task)));
    taskList.append(fragment);
  } catch (error) {
    taskCount.textContent = "";
    listMessage.textContent = error.message;
  }
}

function resetForm() {
  editingTaskId = null;
  editingTaskCompleted = false;
  taskForm.reset();
  priorityInput.value = "medium";
  formHeading.textContent = "Add a task";
  submitButton.textContent = "Add task";
  cancelEditButton.hidden = true;
  showFormError("");
}

function startEditing(task) {
  editingTaskId = task.id;
  editingTaskCompleted = task.completed;
  titleInput.value = task.title;
  descriptionInput.value = task.description || "";
  priorityInput.value = task.priority;
  dueDateInput.value = task.due_date || "";
  formHeading.textContent = "Edit task";
  submitButton.textContent = "Save changes";
  cancelEditButton.hidden = false;
  showFormError("");
  titleInput.focus();
  document.querySelector(".form-panel").scrollIntoView({ behavior: "smooth", block: "start" });
}

function formPayload(completed = editingTaskCompleted) {
  return {
    title: titleInput.value.trim(),
    description: descriptionInput.value || null,
    priority: priorityInput.value,
    due_date: dueDateInput.value || null,
    completed,
  };
}

function taskPayload(task, completed) {
  return {
    title: task.title,
    description: task.description,
    priority: task.priority,
    due_date: task.due_date,
    completed,
  };
}

async function toggleTask(task, completed) {
  try {
    await requestJson(`/api/tasks/${task.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(taskPayload(task, completed)),
    });
    await loadTasks();
  } catch (error) {
    await loadTasks();
    listMessage.hidden = false;
    listMessage.textContent = error.message;
  }
}

async function deleteTask(task) {
  if (!window.confirm(`Delete “${task.title}”? This cannot be undone.`)) {
    return;
  }
  try {
    await requestJson(`/api/tasks/${task.id}`, { method: "DELETE" });
    if (editingTaskId === task.id) {
      resetForm();
    }
    await loadTasks();
  } catch (error) {
    listMessage.hidden = false;
    listMessage.textContent = error.message;
  }
}

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (requestInProgress) {
    return;
  }
  showFormError("");
  requestInProgress = true;
  submitButton.disabled = true;
  try {
    const editing = editingTaskId !== null;
    const payload = formPayload();
    if (!editing) {
      delete payload.completed;
    }
    await requestJson(editing ? `/api/tasks/${editingTaskId}` : "/api/tasks", {
      method: editing ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    resetForm();
    await loadTasks();
  } catch (error) {
    showFormError(error.message);
  } finally {
    requestInProgress = false;
    submitButton.disabled = false;
  }
});

cancelEditButton.addEventListener("click", resetForm);
statusFilter.addEventListener("change", loadTasks);
sortOrder.addEventListener("change", loadTasks);
loadTasks();
