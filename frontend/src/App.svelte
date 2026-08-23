<script>
  import { onMount } from "svelte";
  import KanbanColumn from "./lib/KanbanColumn.svelte";
  import { fetchAchievements, updateState } from "./lib/api.js";

  let achievements = [];
  let loading = true;
  let error = null;
  let achievement_count = "";

  const COLUMNS = [
    { id: "backlog", title: "Backlog", color: "#64748b" },
    { id: "todo",    title: "To Do",   color: "#3b82f6" },
    { id: "done",    title: "Done",    color: "#22c55e" },
  ];

  $: byState = Object.fromEntries(
    COLUMNS.map((col) => [
      col.id,
      achievements.filter((a) => a.state === col.id),
    ])
  );

  onMount(async () => {
    await load();
  });

  async function load() {
    loading = true;
    error = null;
    try {
      achievements = await fetchAchievements();
      const total = achievements.length;
      const done  = achievements.filter((a) => a.state === "done").length;
      achievement_count = `${done} / ${total} achievements`;
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  async function handleMove(api_name, newState) {
    // Optimistic update
    achievements = achievements.map((a) =>
      a.api_name === api_name ? { ...a, state: newState } : a
    );
    try {
      await updateState(api_name, newState);
    } catch (e) {
      error = e.message;
      // Revert on failure
      await load();
    }
  }
</script>

<main>
  <header>
    <div class="header-inner">
      <div class="title-block">
        <h1>🏹 CK3 Achievement Hunt</h1>
        {#if !loading && !error}
          <span class="subtitle">{achievement_count}</span>
        {/if}
      </div>
      <button class="refresh-btn" on:click={load} disabled={loading}>
        {loading ? "Loading…" : "↻ Refresh"}
      </button>
    </div>
  </header>

  {#if error}
    <div class="error-banner">
      <strong>Error:</strong> {error}
      <button on:click={load}>Retry</button>
    </div>
  {/if}

  {#if loading}
    <div class="loader">
      <div class="spinner"></div>
      <p>Fetching achievements from Steam…</p>
    </div>
  {:else if !error}
    <div class="board">
      {#each COLUMNS as col}
        <KanbanColumn
          title={col.title}
          color={col.color}
          achievements={byState[col.id] ?? []}
          onMove={handleMove}
        />
      {/each}
    </div>
  {/if}
</main>

<style>
  :global(*, *::before, *::after) {
    box-sizing: border-box;
  }
  :global(body) {
    margin: 0;
    background: #0d1117;
    color: #e2e8f0;
    font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
  }

  main {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }

  header {
    background: #151b27;
    border-bottom: 1px solid #2e3548;
    padding: 0 24px;
    position: sticky;
    top: 0;
    z-index: 10;
  }
  .header-inner {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 60px;
  }
  .title-block {
    display: flex;
    align-items: baseline;
    gap: 14px;
  }
  h1 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 700;
    color: #f1f5f9;
  }
  .subtitle {
    font-size: 0.82rem;
    color: #64748b;
  }
  .refresh-btn {
    background: #1e2d40;
    border: 1px solid #2e3548;
    color: #93c5fd;
    padding: 6px 16px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    transition: background 0.15s;
  }
  .refresh-btn:hover:not(:disabled) {
    background: #243447;
  }
  .refresh-btn:disabled {
    opacity: 0.5;
    cursor: default;
  }

  .error-banner {
    background: #3b0d0d;
    border: 1px solid #7f1d1d;
    color: #fca5a5;
    padding: 10px 24px;
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 0.85rem;
  }
  .error-banner button {
    background: #7f1d1d;
    color: #fca5a5;
    border: none;
    padding: 3px 10px;
    border-radius: 4px;
    cursor: pointer;
  }

  .loader {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 16px;
    color: #64748b;
  }
  .spinner {
    width: 36px;
    height: 36px;
    border: 3px solid #2e3548;
    border-top-color: #3b82f6;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }

  .board {
    display: flex;
    gap: 18px;
    padding: 20px 24px;
    flex: 1;
    max-width: 1400px;
    margin: 0 auto;
    width: 100%;
    overflow-x: auto;
  }
</style>
