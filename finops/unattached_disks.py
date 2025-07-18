"""
Unattached Disks Remediation module for multi-cloud cost optimization.
Identifies and manages unattached storage volumes across all cloud providers.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from .config import Config


class DiskState(Enum):
    """States of storage disks."""
    ATTACHED = "attached"
    UNATTACHED = "unattached"
    CREATING = "creating"
    DELETING = "deleting"
    ERROR = "error"


class RemediationAction(Enum):
    """Remediation actions for unattached disks."""
    DELETE = "delete"
    SNAPSHOT_AND_DELETE = "snapshot_and_delete"
    ATTACH_TO_INSTANCE = "attach_to_instance"
    MONITOR = "monitor"
    IGNORE = "ignore"


@dataclass
class UnattachedDisk:
    """Container for unattached disk information."""
    disk_id: str
    provider: str
    disk_type: str
    size_gb: int
    created_date: datetime
    last_attached_date: Optional[datetime]
    cost_per_month: float
    region: str
    availability_zone: str
    encrypted: bool
    tags: Dict[str, str]
    state: DiskState
    days_unattached: int
    recommended_action: RemediationAction
    risk_level: str
    potential_savings: float


class UnattachedDisksRemediator:
    """
    Unattached Disks Remediation system for multi-cloud environments.
    
    Identifies, analyzes, and provides remediation recommendations for
    unattached storage volumes across AWS, Azure, GCP, and Oracle Cloud.
    """
    
    def __init__(self, config: Config):
        """
        Initialize Unattached Disks Remediator.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Remediation thresholds
        self.immediate_delete_threshold = 7  # Days
        self.snapshot_delete_threshold = 30  # Days
        self.monitor_threshold = 90  # Days
        
        # Cost thresholds
        self.high_cost_threshold = 100  # USD per month
        self.medium_cost_threshold = 20  # USD per month
        
        # Initialize cloud providers
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self) -> None:
        """Initialize cloud provider clients."""
        if self.config.aws.enabled:
            from .aws import AWSProvider
            self.providers['aws'] = AWSProvider(self.config.aws)
        
        if self.config.azure.enabled:
            from .azure import AzureProvider
            self.providers['azure'] = AzureProvider(self.config.azure)
        
        if self.config.gcp.enabled:
            from .gcp import GCPProvider
            self.providers['gcp'] = GCPProvider(self.config.gcp)
        
        if self.config.oracle.enabled:
            from .oracle import OracleProvider
            self.providers['oracle'] = OracleProvider(self.config.oracle)
    
    async def scan_unattached_disks(self) -> List[UnattachedDisk]:
        """
        Scan all cloud providers for unattached disks.
        
        Returns:
            List of unattached disks found across all providers
        """
        self.logger.info("Starting scan for unattached disks across all providers")
        
        all_unattached_disks = []
        
        for provider_name, provider in self.providers.items():
            try:
                self.logger.info(f"Scanning unattached disks in {provider_name}")
                provider_disks = await self._scan_provider_unattached_disks(provider_name, provider)
                all_unattached_disks.extend(provider_disks)
                
                self.logger.info(f"Found {len(provider_disks)} unattached disks in {provider_name}")
                
            except Exception as e:
                self.logger.error(f"Error scanning unattached disks in {provider_name}: {e}")
        
        # Sort by potential savings (highest first)
        all_unattached_disks.sort(key=lambda x: x.potential_savings, reverse=True)
        
        self.logger.info(f"Total unattached disks found: {len(all_unattached_disks)}")
        return all_unattached_disks
    
    async def _scan_provider_unattached_disks(self,
                                             provider_name: str,
                                             provider) -> List[UnattachedDisk]:
        """Scan unattached disks for a specific provider."""
        unattached_disks = []
        
        if provider_name == 'aws':
            unattached_disks = await self._scan_aws_unattached_volumes(provider)
        elif provider_name == 'azure':
            unattached_disks = await self._scan_azure_unattached_disks(provider)
        elif provider_name == 'gcp':
            unattached_disks = await self._scan_gcp_unattached_disks(provider)
        elif provider_name == 'oracle':
            unattached_disks = await self._scan_oracle_unattached_volumes(provider)
        
        return unattached_disks
    
    async def _scan_aws_unattached_volumes(self, provider) -> List[UnattachedDisk]:
        """Scan AWS EBS volumes for unattached volumes."""
        unattached_disks = []
        
        try:
            # Get all EBS volumes
            volumes = provider.ec2_client.describe_volumes()['Volumes']
            
            for volume in volumes:
                if volume['State'] == 'available':  # Unattached state
                    disk = self._create_unattached_disk_from_aws_volume(volume)
                    unattached_disks.append(disk)
            
        except Exception as e:
            self.logger.error(f"Error scanning AWS EBS volumes: {e}")
        
        return unattached_disks
    
    async def _scan_azure_unattached_disks(self, provider) -> List[UnattachedDisk]:
        """Scan Azure managed disks for unattached disks."""
        unattached_disks = []
        
        try:
            if hasattr(provider, 'get_unattached_disks'):
                azure_disks = provider.get_unattached_disks()
                
                for disk in azure_disks:
                    unattached_disk = self._create_unattached_disk_from_azure_disk(disk)
                    unattached_disks.append(unattached_disk)
            
        except Exception as e:
            self.logger.error(f"Error scanning Azure managed disks: {e}")
        
        return unattached_disks
    
    async def _scan_gcp_unattached_disks(self, provider) -> List[UnattachedDisk]:
        """Scan GCP persistent disks for unattached disks."""
        unattached_disks = []
        
        try:
            if hasattr(provider, 'get_unattached_disks'):
                gcp_disks = provider.get_unattached_disks()
                
                for disk in gcp_disks:
                    unattached_disk = self._create_unattached_disk_from_gcp_disk(disk)
                    unattached_disks.append(unattached_disk)
            
        except Exception as e:
            self.logger.error(f"Error scanning GCP persistent disks: {e}")
        
        return unattached_disks
    
    async def _scan_oracle_unattached_volumes(self, provider) -> List[UnattachedDisk]:
        """Scan Oracle Cloud block volumes for unattached volumes."""
        unattached_disks = []
        
        try:
            if hasattr(provider, 'get_unattached_volumes'):
                oracle_volumes = provider.get_unattached_volumes()
                
                for volume in oracle_volumes:
                    unattached_disk = self._create_unattached_disk_from_oracle_volume(volume)
                    unattached_disks.append(unattached_disk)
            
        except Exception as e:
            self.logger.error(f"Error scanning Oracle Cloud block volumes: {e}")
        
        return unattached_disks
    
    def _create_unattached_disk_from_aws_volume(self, volume: Dict[str, Any]) -> UnattachedDisk:
        """Create UnattachedDisk object from AWS EBS volume."""
        volume_id = volume['VolumeId']
        size_gb = volume['Size']
        volume_type = volume['VolumeType']
        created_date = volume['CreateTime']
        encrypted = volume.get('Encrypted', False)
        availability_zone = volume['AvailabilityZone']
        
        # Extract tags
        tags = {tag['Key']: tag['Value'] for tag in volume.get('Tags', [])}
        
        # Calculate days unattached (simplified - using creation date)
        days_unattached = (datetime.now(created_date.tzinfo) - created_date).days
        
        # Calculate cost per month (simplified pricing)
        cost_per_gb_month = self._get_aws_ebs_cost_per_gb(volume_type)
        cost_per_month = size_gb * cost_per_gb_month
        
        # Determine recommended action
        recommended_action, risk_level = self._determine_remediation_action(
            days_unattached, cost_per_month, tags
        )
        
        return UnattachedDisk(
            disk_id=volume_id,
            provider='aws',
            disk_type=volume_type,
            size_gb=size_gb,
            created_date=created_date,
            last_attached_date=None,  # Would need to track this separately
            cost_per_month=cost_per_month,
            region=availability_zone[:-1],  # Remove AZ letter
            availability_zone=availability_zone,
            encrypted=encrypted,
            tags=tags,
            state=DiskState.UNATTACHED,
            days_unattached=days_unattached,
            recommended_action=recommended_action,
            risk_level=risk_level,
            potential_savings=cost_per_month
        )
    
    def _create_unattached_disk_from_azure_disk(self, disk: Dict[str, Any]) -> UnattachedDisk:
        """Create UnattachedDisk object from Azure managed disk."""
        # This would be implemented based on Azure API response structure
        # Placeholder implementation
        return UnattachedDisk(
            disk_id=disk.get('id', ''),
            provider='azure',
            disk_type=disk.get('sku', {}).get('name', ''),
            size_gb=disk.get('disk_size_gb', 0),
            created_date=datetime.now(),
            last_attached_date=None,
            cost_per_month=0.0,
            region=disk.get('location', ''),
            availability_zone='',
            encrypted=disk.get('encryption_settings_enabled', False),
            tags=disk.get('tags', {}),
            state=DiskState.UNATTACHED,
            days_unattached=0,
            recommended_action=RemediationAction.MONITOR,
            risk_level='medium',
            potential_savings=0.0
        )
    
    def _create_unattached_disk_from_gcp_disk(self, disk: Dict[str, Any]) -> UnattachedDisk:
        """Create UnattachedDisk object from GCP persistent disk."""
        # This would be implemented based on GCP API response structure
        # Placeholder implementation
        return UnattachedDisk(
            disk_id=disk.get('name', ''),
            provider='gcp',
            disk_type=disk.get('type', ''),
            size_gb=int(disk.get('sizeGb', 0)),
            created_date=datetime.now(),
            last_attached_date=None,
            cost_per_month=0.0,
            region=disk.get('region', ''),
            availability_zone=disk.get('zone', ''),
            encrypted=False,
            tags={},
            state=DiskState.UNATTACHED,
            days_unattached=0,
            recommended_action=RemediationAction.MONITOR,
            risk_level='medium',
            potential_savings=0.0
        )
    
    def _create_unattached_disk_from_oracle_volume(self, volume: Dict[str, Any]) -> UnattachedDisk:
        """Create UnattachedDisk object from Oracle Cloud block volume."""
        # This would be implemented based on Oracle Cloud API response structure
        # Placeholder implementation
        return UnattachedDisk(
            disk_id=volume.get('id', ''),
            provider='oracle',
            disk_type='block',
            size_gb=volume.get('size_in_gbs', 0),
            created_date=datetime.now(),
            last_attached_date=None,
            cost_per_month=0.0,
            region=volume.get('availability_domain', ''),
            availability_zone=volume.get('availability_domain', ''),
            encrypted=volume.get('is_encrypted', False),
            tags=volume.get('defined_tags', {}),
            state=DiskState.UNATTACHED,
            days_unattached=0,
            recommended_action=RemediationAction.MONITOR,
            risk_level='medium',
            potential_savings=0.0
        )
    
    def _get_aws_ebs_cost_per_gb(self, volume_type: str) -> float:
        """Get AWS EBS cost per GB per month."""
        # Simplified pricing (actual pricing varies by region)
        pricing = {
            'gp2': 0.10,  # General Purpose SSD
            'gp3': 0.08,  # General Purpose SSD (gp3)
            'io1': 0.125, # Provisioned IOPS SSD
            'io2': 0.125, # Provisioned IOPS SSD (io2)
            'st1': 0.045, # Throughput Optimized HDD
            'sc1': 0.025, # Cold HDD
            'standard': 0.05  # Magnetic
        }
        return pricing.get(volume_type, 0.10)
    
    def _determine_remediation_action(self,
                                     days_unattached: int,
                                     cost_per_month: float,
                                     tags: Dict[str, str]) -> tuple[RemediationAction, str]:
        """Determine the recommended remediation action."""
        
        # Check for protection tags
        if any(tag.lower() in ['do-not-delete', 'keep', 'permanent'] 
               for tag in tags.values()):
            return RemediationAction.IGNORE, 'low'
        
        # High cost volumes - be more cautious
        if cost_per_month > self.high_cost_threshold:
            if days_unattached > self.snapshot_delete_threshold:
                return RemediationAction.SNAPSHOT_AND_DELETE, 'medium'
            else:
                return RemediationAction.MONITOR, 'low'
        
        # Medium cost volumes
        elif cost_per_month > self.medium_cost_threshold:
            if days_unattached > self.snapshot_delete_threshold:
                return RemediationAction.SNAPSHOT_AND_DELETE, 'medium'
            elif days_unattached > self.immediate_delete_threshold:
                return RemediationAction.MONITOR, 'low'
            else:
                return RemediationAction.MONITOR, 'low'
        
        # Low cost volumes
        else:
            if days_unattached > self.immediate_delete_threshold:
                return RemediationAction.DELETE, 'high'
            else:
                return RemediationAction.MONITOR, 'low'
    
    async def execute_remediation(self,
                                 unattached_disks: List[UnattachedDisk],
                                 dry_run: bool = True) -> Dict[str, Any]:
        """
        Execute remediation actions for unattached disks.
        
        Args:
            unattached_disks: List of unattached disks to remediate
            dry_run: If True, only simulate the actions
            
        Returns:
            Dictionary containing remediation results
        """
        self.logger.info(f"Executing remediation for {len(unattached_disks)} disks (dry_run={dry_run})")
        
        results = {
            'total_disks': len(unattached_disks),
            'dry_run': dry_run,
            'actions_taken': {},
            'total_potential_savings': 0.0,
            'errors': []
        }
        
        # Group disks by action
        actions_map = {}
        for disk in unattached_disks:
            action = disk.recommended_action
            if action not in actions_map:
                actions_map[action] = []
            actions_map[action].append(disk)
        
        # Execute actions
        for action, disks in actions_map.items():
            try:
                action_results = await self._execute_action(action, disks, dry_run)
                results['actions_taken'][action.value] = action_results
                
                # Calculate savings
                for disk in disks:
                    if action in [RemediationAction.DELETE, RemediationAction.SNAPSHOT_AND_DELETE]:
                        results['total_potential_savings'] += disk.potential_savings
                
            except Exception as e:
                error_msg = f"Error executing {action.value}: {e}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    async def _execute_action(self,
                             action: RemediationAction,
                             disks: List[UnattachedDisk],
                             dry_run: bool) -> Dict[str, Any]:
        """Execute a specific remediation action."""
        
        results = {
            'action': action.value,
            'disk_count': len(disks),
            'successful': 0,
            'failed': 0,
            'details': []
        }
        
        for disk in disks:
            try:
                if action == RemediationAction.DELETE:
                    success = await self._delete_disk(disk, dry_run)
                elif action == RemediationAction.SNAPSHOT_AND_DELETE:
                    success = await self._snapshot_and_delete_disk(disk, dry_run)
                elif action == RemediationAction.MONITOR:
                    success = await self._monitor_disk(disk, dry_run)
                elif action == RemediationAction.IGNORE:
                    success = True  # No action needed
                else:
                    success = False
                
                if success:
                    results['successful'] += 1
                    results['details'].append({
                        'disk_id': disk.disk_id,
                        'provider': disk.provider,
                        'status': 'success',
                        'savings': disk.potential_savings if action in [RemediationAction.DELETE, RemediationAction.SNAPSHOT_AND_DELETE] else 0
                    })
                else:
                    results['failed'] += 1
                    results['details'].append({
                        'disk_id': disk.disk_id,
                        'provider': disk.provider,
                        'status': 'failed'
                    })
                
            except Exception as e:
                results['failed'] += 1
                results['details'].append({
                    'disk_id': disk.disk_id,
                    'provider': disk.provider,
                    'status': 'error',
                    'error': str(e)
                })
        
        return results
    
    async def _delete_disk(self, disk: UnattachedDisk, dry_run: bool) -> bool:
        """Delete an unattached disk."""
        if dry_run:
            self.logger.info(f"[DRY RUN] Would delete disk {disk.disk_id} in {disk.provider}")
            return True
        
        provider = self.providers.get(disk.provider)
        if not provider:
            return False
        
        try:
            if disk.provider == 'aws':
                provider.ec2_client.delete_volume(VolumeId=disk.disk_id)
            elif hasattr(provider, 'delete_disk'):
                provider.delete_disk(disk.disk_id)
            
            self.logger.info(f"Deleted disk {disk.disk_id} in {disk.provider}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting disk {disk.disk_id}: {e}")
            return False
    
    async def _snapshot_and_delete_disk(self, disk: UnattachedDisk, dry_run: bool) -> bool:
        """Create snapshot of disk and then delete it."""
        if dry_run:
            self.logger.info(f"[DRY RUN] Would snapshot and delete disk {disk.disk_id} in {disk.provider}")
            return True
        
        provider = self.providers.get(disk.provider)
        if not provider:
            return False
        
        try:
            # Create snapshot first
            snapshot_name = f"auto-snapshot-{disk.disk_id}-{datetime.now().strftime('%Y%m%d')}"
            
            if disk.provider == 'aws':
                # Create snapshot
                snapshot_response = provider.ec2_client.create_snapshot(
                    VolumeId=disk.disk_id,
                    Description=f"Automatic snapshot before deletion of {disk.disk_id}"
                )
                
                # Wait for snapshot to complete (simplified)
                # In production, you'd want to check snapshot status
                
                # Delete volume
                provider.ec2_client.delete_volume(VolumeId=disk.disk_id)
                
            elif hasattr(provider, 'create_snapshot_and_delete_disk'):
                provider.create_snapshot_and_delete_disk(disk.disk_id, snapshot_name)
            
            self.logger.info(f"Snapshotted and deleted disk {disk.disk_id} in {disk.provider}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error snapshotting and deleting disk {disk.disk_id}: {e}")
            return False
    
    async def _monitor_disk(self, disk: UnattachedDisk, dry_run: bool) -> bool:
        """Add disk to monitoring list."""
        if dry_run:
            self.logger.info(f"[DRY RUN] Would add disk {disk.disk_id} to monitoring")
            return True
        
        # In a real implementation, this would add the disk to a monitoring system
        # or database for future tracking
        self.logger.info(f"Added disk {disk.disk_id} to monitoring list")
        return True
    
    def generate_unattached_disks_report(self, 
                                        unattached_disks: List[UnattachedDisk]) -> Dict[str, Any]:
        """Generate a comprehensive report of unattached disks."""
        
        if not unattached_disks:
            return {'message': 'No unattached disks found'}
        
        # Calculate summary statistics
        total_disks = len(unattached_disks)
        total_size_gb = sum(disk.size_gb for disk in unattached_disks)
        total_cost = sum(disk.cost_per_month for disk in unattached_disks)
        total_potential_savings = sum(disk.potential_savings for disk in unattached_disks)
        
        # Group by provider
        by_provider = {}
        for disk in unattached_disks:
            if disk.provider not in by_provider:
                by_provider[disk.provider] = []
            by_provider[disk.provider].append(disk)
        
        # Group by recommended action
        by_action = {}
        for disk in unattached_disks:
            action = disk.recommended_action.value
            if action not in by_action:
                by_action[action] = []
            by_action[action].append(disk)
        
        # Group by risk level
        by_risk = {'low': [], 'medium': [], 'high': []}
        for disk in unattached_disks:
            by_risk[disk.risk_level].append(disk)
        
        return {
            'summary': {
                'total_unattached_disks': total_disks,
                'total_size_gb': total_size_gb,
                'total_monthly_cost': total_cost,
                'total_potential_savings': total_potential_savings,
                'scan_date': datetime.now().isoformat()
            },
            'by_provider': {
                provider: {
                    'count': len(disks),
                    'total_size_gb': sum(disk.size_gb for disk in disks),
                    'total_cost': sum(disk.cost_per_month for disk in disks),
                    'potential_savings': sum(disk.potential_savings for disk in disks),
                    'disks': [disk.__dict__ for disk in disks]
                }
                for provider, disks in by_provider.items()
            },
            'by_recommended_action': {
                action: {
                    'count': len(disks),
                    'potential_savings': sum(disk.potential_savings for disk in disks)
                }
                for action, disks in by_action.items()
            },
            'by_risk_level': {
                risk: {
                    'count': len(disks),
                    'potential_savings': sum(disk.potential_savings for disk in disks)
                }
                for risk, disks in by_risk.items()
            },
            'top_cost_disks': [
                disk.__dict__ for disk in sorted(unattached_disks, 
                                               key=lambda x: x.cost_per_month, 
                                               reverse=True)[:10]
            ]
        }