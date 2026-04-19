interface PageHeaderProps {
  title: string;
  subtitle: string;
  rightSlot?: React.ReactNode;
}

function PageHeader({ title, subtitle, rightSlot }: PageHeaderProps) {
  return (
    <header className="page-header">
      <div>
        <h2>{title}</h2>
        <p>{subtitle}</p>
      </div>
      {rightSlot ? <div>{rightSlot}</div> : null}
    </header>
  );
}

export default PageHeader;
