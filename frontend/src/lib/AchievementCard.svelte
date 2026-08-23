<script>
  export let achievement;
  export let onMove;

  const STATES = ["backlog", "todo", "done"];
  const LABELS = { backlog: "Backlog", todo: "To Do", done: "Done" };

  function move(newState) {
    onMove(achievement.api_name, newState);
  }
</script>

<div class="card" class:achieved={achievement.achieved}>
  <div class="card-header">
    {#if achievement.icon}
      <img
        src={achievement.achieved ? achievement.icon : achievement.icon_gray}
        alt={achievement.display_name}
        class="icon"
        loading="lazy"
      />
    {/if}
    <div class="card-title">
      <span class="name">{achievement.display_name}</span>
      {#if achievement.achieved}
        <span class="badge done-badge">✔ Unlocked</span>
      {/if}
    </div>
  </div>
  {#if achievement.description}
    <p class="description">{achievement.description}</p>
  {/if}
  <p class="percent">
    <span class="percent-bar" style="width: {Math.min(achievement.global_percent, 100)}%"></span>
    <span class="percent-label">{achievement.global_percent}% of players</span>
  </p>
  <div class="actions">
    {#each STATES.filter((s) => s !== achievement.state) as s}
      <button class="move-btn {s}" on:click={() => move(s)}>
        → {LABELS[s]}
      </button>
    {/each}
  </div>
</div>

<style>
  .card {
    background: #1e2330;
    border: 1px solid #2e3548;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;
    transition: box-shadow 0.15s;
  }
  .card:hover {
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.4);
  }
  .card.achieved {
    border-left: 3px solid #4ade80;
  }
  .card-header {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 6px;
  }
  .icon {
    width: 40px;
    height: 40px;
    border-radius: 4px;
    flex-shrink: 0;
  }
  .card-title {
    display: flex;
    flex-direction: column;
    gap: 3px;
  }
  .name {
    font-weight: 600;
    font-size: 0.9rem;
    color: #e2e8f0;
    line-height: 1.3;
  }
  .badge {
    font-size: 0.7rem;
    padding: 1px 6px;
    border-radius: 4px;
    width: fit-content;
  }
  .done-badge {
    background: #14532d;
    color: #4ade80;
  }
  .description {
    font-size: 0.78rem;
    color: #94a3b8;
    margin: 0 0 8px 0;
    line-height: 1.4;
  }
  .percent {
    position: relative;
    margin: 0 0 10px 0;
    height: 16px;
    background: #2e3548;
    border-radius: 4px;
    overflow: hidden;
    display: flex;
    align-items: center;
  }
  .percent-bar {
    position: absolute;
    left: 0;
    top: 0;
    height: 100%;
    background: #1e3a5f;
    border-radius: 4px;
    transition: width 0.3s;
  }
  .percent-label {
    position: relative;
    font-size: 0.68rem;
    color: #93c5fd;
    padding: 0 6px;
    z-index: 1;
  }
  .actions {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }
  .move-btn {
    font-size: 0.72rem;
    padding: 3px 9px;
    border-radius: 5px;
    border: none;
    cursor: pointer;
    font-weight: 500;
    transition: opacity 0.15s;
  }
  .move-btn:hover {
    opacity: 0.85;
  }
  .move-btn.backlog {
    background: #374151;
    color: #d1d5db;
  }
  .move-btn.todo {
    background: #1e3a5f;
    color: #93c5fd;
  }
  .move-btn.done {
    background: #14532d;
    color: #4ade80;
  }
</style>
