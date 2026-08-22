<script>
  import AchievementCard from "./AchievementCard.svelte";
  export let title;
  export let color;
  export let achievements = [];
  export let onMove;
</script>

<div class="column">
  <div class="column-header" style="--col-color: {color}">
    <h2>{title}</h2>
    <span class="count">{achievements.length}</span>
  </div>
  <div class="cards">
    {#if achievements.length === 0}
      <p class="empty">No achievements here yet.</p>
    {/if}
    {#each achievements as ach (ach.api_name)}
      <AchievementCard achievement={ach} {onMove} />
    {/each}
  </div>
</div>

<style>
  .column {
    background: #151b27;
    border-radius: 10px;
    border: 1px solid #2e3548;
    display: flex;
    flex-direction: column;
    min-width: 300px;
    flex: 1;
    max-height: calc(100vh - 120px);
  }
  .column-header {
    padding: 14px 16px 10px;
    border-bottom: 2px solid var(--col-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-shrink: 0;
  }
  h2 {
    margin: 0;
    font-size: 1rem;
    font-weight: 700;
    color: var(--col-color);
    text-transform: uppercase;
    letter-spacing: 0.06em;
  }
  .count {
    background: #2e3548;
    color: #94a3b8;
    border-radius: 99px;
    padding: 1px 9px;
    font-size: 0.78rem;
    font-weight: 600;
  }
  .cards {
    padding: 12px;
    overflow-y: auto;
    flex: 1;
  }
  .cards::-webkit-scrollbar {
    width: 5px;
  }
  .cards::-webkit-scrollbar-thumb {
    background: #2e3548;
    border-radius: 99px;
  }
  .empty {
    color: #4b5563;
    font-size: 0.82rem;
    text-align: center;
    margin-top: 24px;
  }
</style>
